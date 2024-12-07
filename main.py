# main.py

from fastapi import (
    FastAPI,
    Request,
    Form,
    HTTPException,
    Depends,
    status,
    Query,
    Response,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta, timezone
import httpx
from sqlalchemy import and_
import json
from models import User, Record, Role, EmailSubmission
from database import get_db
from sqlalchemy.orm import Session
import requests
from sqlalchemy.exc import IntegrityError
import config
from typing import Optional
import email
from email import policy
import logging
import jwt
import hashlib
from datetime import datetime, timedelta
from math import ceil
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # 日志输出到控制台
)


# 关闭所有doc的接口
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# # 配置允许的前端域名
# origins = [
#     "https://your-frontend-domain.com",  # 替换为您的前端域名
#     # 如果有多个前端域名，可以在这里添加
# ]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,  # 允许的源
    allow_credentials=True,  # 允许发送 Cookie
    allow_methods=["*"],  # 允许的 HTTP 方法
    allow_headers=["*"],  # 允许的 HTTP 头
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化模板
templates = Jinja2Templates(directory="templates")


# 发送邮件的函数
def post_email(data, domin, api: str):
    """
    Send a POST request to an external URL with email data.
    """
    url = f"https://api.mailgun.net/v3/{domin}/messages"
    return requests.post(
        url,
        auth=("api", api),
        data=data,
    )


# 提取邮件正文的函数
def extract_body_recursive(message):
    parts = []
    if message.is_multipart():
        # 遍历多部分邮件
        for part in message.iter_parts():
            parts.extend(extract_body_recursive(part))  # 递归提取子部分
    else:
        # 处理单个部分
        content_type = message.get_content_type()
        charset = message.get_content_charset() or "utf-8"
        try:
            payload = message.get_payload(decode=True)
            if payload:  # 检查是否有内容
                parts.append((content_type, payload.decode(charset)))
        except (UnicodeDecodeError, AttributeError):
            # 处理解码错误
            parts.append(
                (content_type, f"Error decoding content with charset {charset}")
            )

    return parts


# 写入邮件到数据库
def write_email_to_db(username: str, data: dict, db: Session):
    """
    Write email data to the database.
    """
    # User data
    username = username.split("@")
    record = Record(
        email_user=username[0],
        email_domain=username[-1],
        subject=data.get("subject", ""),
        from_field=data.get("from", ""),
        text_plain=data.get("text/plain", ""),
        text_html=data.get("text/html", ""),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# 密码哈希
def hash_password(password: str) -> str:
    hash_password = hashlib.sha256(password.encode()).hexdigest()
    return hash_password


# 创建 JWT Token
async def create_access_token(data: dict, expire: timedelta) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithms)
    return encoded_jwt


# 验证用户
def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名或密码不能为空")
    if username and password:
        user = db.query(User).filter(User.username == username).first()
        if user and user.password == hash_password(password):
            return user
    return None


# 依赖项：获取当前用户
async def get_current_user(request: Request):

    token = request.cookies.get("access_token")
    if not token:
        raise RedirectToLoginException()
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithms])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if not username or not role:
            raise RedirectToLoginException()
    except:
        raise RedirectToLoginException()

    return {"username": username, "role": role}


#  自定义异常
class RedirectToLoginException(Exception):
    def __init__(self, redirect_url: str = "/login"):
        self.redirect_url = redirect_url


# 异常处理器：处理 RedirectToLoginException
@app.exception_handler(RedirectToLoginException)
async def redirect_to_login_handler(request: Request, exc: RedirectToLoginException):
    # 使用 303 See Other 确保浏览器使用 GET 方法
    return RedirectResponse(url=exc.redirect_url, status_code=status.HTTP_303_SEE_OTHER)


# 其他异常处理器（可选）
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    print(f"HTTP Exception: {exc}")

    return RedirectResponse(url="/404")


# 路由：404 页面
@app.get("/404", response_class=HTMLResponse)
async def not_found(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})


# 路由：主页（需要登录）
@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    if not user:
        raise RedirectToLoginException()
    emails = db.query(Role).filter(Role.role == user.get("role", "guise")).all()
    emails_options = [email.email.replace("@", "") for email in emails if emails]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "username": "",
            "emails_options": emails_options,
            "code": "\n".join(emails_options),
        },
    )


# 路由：搜索用户
@app.post("/search", response_class=HTMLResponse)
def search_user(
    request: Request,
    username: str = Form(...),
    emails: str = Form(...),
    currentuser=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Handle the search form submission and display user data.
    """
    if not currentuser:
        raise RedirectToLoginException()
    email_user = username.strip().lower()
    email_domain = emails.strip()

    # 同时查询用户的邮件记录，条件都要满足
    emails = db.query(Role).filter(Role.role == currentuser.get("role", "guise")).all()
    emails_options = [email.email.replace("@", "") for email in emails if emails]

    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    records = (
        db.query(Record)
        .filter(
            and_(
                Record.email_user == email_user,
                Record.email_domain == email_domain,
                Record.created_at >= one_day_ago,
            )
        )
        .all()
    )
    message = None

    if not records:
        message = f"No data found for user '{email_user}@{email_domain}'."

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": currentuser,
            "emails_options": emails_options,
            "records": records,
            "email_domin": f"{email_user}@{email_domain}",
            "message": message,
        },
    )


@app.get("/record/{record_id}", response_class=HTMLResponse)
def display_record(
    request: Request,
    record_id: int,
    email_domin: str = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Display concatenated text/plain and text/html for a specific record.
    """
    if not current_user:
        raise RedirectToLoginException()
    # Fetch the record with the associated user
    email_data = email_domin.strip().split("@")
    record = (
        db.query(Record)
        .filter(
            and_(
                Record.id == record_id,
                Record.email_user == email_data[0],
                Record.email_domain == email_data[-1],
            )
        )
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")

    # Concatenate text/plain and text/html
    concatenated_content = f"<p>{record.text_plain}</p>\n{record.text_html}"
    subject = record.subject
    return templates.TemplateResponse(
        "display_record.html",
        {"request": request, "content": concatenated_content, "subject": subject},
    )


# 查询发送邮件记录
@app.get("/resend/{send_id}", response_class=HTMLResponse)
def resend_email(
    request: Request,
    send_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Resend an email submission.
    """
    if not current_user or current_user.get("role", "") != "admin":
        return RedirectResponse(url="/")

    email_submission = (
        db.query(EmailSubmission).filter(EmailSubmission.id == send_id).first()
    )
    if not email_submission:
        raise HTTPException(status_code=404, detail="Email submission not found.")
    concatenated_content = f"{email_submission.html_content}"
    subject = email_submission.subject
    return templates.TemplateResponse(
        "display_record.html",
        {"request": request, "content": concatenated_content, "subject": subject},
    )


# 登录页面
# 路由：登录页面（GET）
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": None,
            "turnstile_site_key": config.turnstile_site_key,  # 传递 Site Key 给模板
        },
    )


# 登录页面
# 路由：处理登录（POST）
@app.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if config.turnstile_site_key:
        turnstile_token = (await request.form()).get("cf-turnstile-response")
        # Verify the Turnstile token with Cloudflare
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={
                    "secret": config.turnstile_secret_key,
                    "response": turnstile_token,
                    "remoteip": request.client.host,  # Optional
                },
            )
        result = resp.json()

        if not result.get("success"):
            # Handle verification failure
            error = "Turnstile verification failed. Please try again."
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": error,
                    "turnstile_site_key": config.turnstile_site_key,
                },
            )

    user = authenticate_user(username, password, db)
    logging.info(f"User: {user}")
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "用户名或密码错误",
                "turnstile_site_key": config.turnstile_site_key,
            },
        )
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=config.access_token_expire_minutes
    )
    access_token = await create_access_token(
        data={"sub": user.username, "role": user.role},
        expire=expires,
    )
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=config.access_token_expire_minutes * 60,
    )
    return response


@app.get("/logout")
async def logout(response: Response):
    # 删除 Cookie，确保删除时与设置时的属性一致
    response.delete_cookie("access_token", path="/", secure=True, samesite="None")

    # 重定向到登录页面
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, user: User = Depends(get_current_user)):
    if not user or user.get("role", "") != "admin":
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "user": user,
            "user_creation_success": None,
            "user_creation_error": None,
            "role_creation_success": None,
            "role_creation_error": None,
        },
    )


@app.post("/admin/create_user", response_class=HTMLResponse)
async def create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    key: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user or current_user.get("role", "") != "admin":
        return RedirectResponse(url="/")
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "user": current_user,
                "user_creation_success": False,
                "user_creation_error": "用户名已存在",
                "role_creation_success": None,
                "role_creation_error": None,
            },
        )

    # 哈希密码
    hashed_password = hash_password(password)

    # 创建新用户
    new_user = User(username=username, password=hashed_password, role=role, key=key)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "user": current_user,
            "user_creation_success": True,
            "user_creation_error": None,
            "role_creation_success": None,
            "role_creation_error": None,
        },
    )


# 路由：创建角色（管理员权限）
@app.post("/admin/create_role", response_class=HTMLResponse)
async def create_role(
    request: Request,
    role: str = Form(...),
    email: str = Form(...),
    key: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user or current_user.get("role", "") != "admin":
        return RedirectResponse(url="/")

    # 创建新角色
    new_role = Role(role=role, email=email, key=key)
    db.add(new_role)
    try:
        db.commit()
        db.refresh(new_role)
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "user": current_user,
                "user_creation_success": None,
                "user_creation_error": None,
                "role_creation_success": False,
                "role_creation_error": "在该角色下，该邮箱已存在",
            },
        )

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "user": current_user,
            "user_creation_success": None,
            "user_creation_error": None,
            "role_creation_success": True,
            "role_creation_error": None,
        },
    )


@app.delete("/delete_role/{roleId}", response_class=HTMLResponse)
async def delete_role(
    request: Request,
    roleId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user or current_user.get("role", "") != "admin":
        return RedirectResponse(url="/")
    role = db.query(Role).filter(Role.id == roleId).first()
    if not role:
        return RedirectResponse(url="/404", status_code=status.HTTP_303_SEE_OTHER)
    db.delete(role)
    db.commit()
    return RedirectResponse(url="/all", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/update_user")
async def update_user(
    request: Request,
    user_id: int = Form(...),
    username: str = Form(...),
    role: str = Form(...),
    password: str = Form(None),
    key: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user or current_user.get("role", "") != "admin":
        return RedirectResponse(url="/")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/404", status_code=status.HTTP_303_SEE_OTHER)
    user.username = username
    user.role = role
    if password:
        user.password = hash_password(password)
    if key:
        user.key = key
    db.commit()
    db.refresh(user)
    return RedirectResponse(url="/all", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/update_role", response_class=HTMLResponse)
async def update_role(
    request: Request,
    role_id: int = Form(...),
    role_name: str = Form(...),
    email: str = Form(...),
    key: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user or current_user.get("role", "") != "admin":
        return RedirectResponse(url="/")
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        return RedirectResponse(url="/404", status_code=status.HTTP_303_SEE_OTHER)
    role.role = role_name
    role.email = email
    if key:
        role.key = key
    print(role.role, role.email, role.id)
    db.commit()
    db.refresh(role)
    return RedirectResponse(url="/all", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/all", response_class=HTMLResponse)
def get_all_users_form(
    request: Request,
    action: Optional[str] = None,
    user_page: int = 1,
    role_page: int = 1,
    record_page: int = 1,
    record_domain: Optional[str] = None,
    send_page: int = 1,
    send_total_pages: int = 1,
    username: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Render a form to input the secret key to access all user data.
    """
    if not current_user or current_user.get("role", "") != "admin":
        return RedirectResponse(url="/")

    # 初始化查询
    users = []
    user_total_pages = 1
    roles = []
    role_total_pages = 1
    records = []
    record_total_pages = 1
    sends = []
    send_total_pages = 1

    if action == "users":
        # 查询所有用户
        users = db.query(User).offset((user_page - 1) * 10).limit(10).all()
        # 计算总记录数和总页数
        total_records = db.query(User).count()
        user_total_pages = ceil(total_records / 10)

    if action == "roles":
        # 查询所有角色
        roles = db.query(Role).offset((role_page - 1) * 10).limit(10).all()
        # 计算总记录数和总页数
        total_records = db.query(Role).count()
        role_total_pages = ceil(total_records / 10)

    if action == "records":
        records_query = db.query(Record)
        if record_domain:
            records_query = records_query.filter(
                Record.email_domain == record_domain.strip()
            )

        # 计算总记录数和总页数
        total_records = db.query(Record).count()
        record_total_pages = ceil(total_records / 10)
        records = records_query.offset((record_page - 1) * 10).limit(10).all()

    if action == "sendemail":
        send_query = db.query(EmailSubmission)
        if username:
            send_query = send_query.filter(EmailSubmission.username == username.strip())
        # 计算总记录数和总页数
        total_records = db.query(EmailSubmission).count()
        send_total_pages = ceil(total_records / 10)
        sends = send_query.offset((send_page - 1) * 10).limit(10).all()

        pass

    return templates.TemplateResponse(
        "all_users.html",
        {
            "request": request,
            "users": users,
            "user_page": user_page,
            "user_total_pages": user_total_pages,
            "role_page": role_page,
            "role_total_pages": role_total_pages,
            "roles": roles,
            "record_page": record_page,
            "record_total_pages": record_total_pages,
            "records": records,
            "send_page": send_page,
            "send_total_pages": send_total_pages,
            "sends": sends,
        },
    )


@app.get("/send-email", response_class=HTMLResponse)
def send_email_form(
    request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Render the email submission form.
    """
    if not user:
        raise RedirectToLoginException()
    emails = db.query(Role).filter(Role.role == user.get("role", "guise")).all()
    emails_options = [
        email.email for email in emails if emails and email.email.startswith("@")
    ]

    return templates.TemplateResponse(
        "send_email.html",
        {
            "request": request,
            "secret_key": "",
            "error": "",
            "success_message": "",
            "priority_options": emails_options,
        },
    )


@app.post("/send-email", response_class=HTMLResponse)
def handle_send_email(
    request: Request,
    secret_key: str = Form(None),
    username: str = Form(...),
    priority: str = Form(...),
    to_field: str = Form(...),
    subject: str = Form(...),
    html_content: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Handle the email submission form.
    """
    if not current_user:
        raise RedirectToLoginException()
    username = username.strip().lower()
    selected_suffix = priority.strip()
    from_field = f"{username}{selected_suffix}"

    user = current_user.get("username", "")

    # if not secret_key:
    #     secret_key = db.query(User).filter(User.username == user).first().key

    emails = db.query(Role).filter(Role.role == current_user.get("role", "guise")).all()
    emails_options = [
        email.email for email in emails if emails and email.email.startswith("@")
    ]

    # Validate all fields are provided
    if not all([username, to_field, subject, html_content]):
        error = "All fields are required."
        return templates.TemplateResponse(
            "send_email.html",
            {
                "request": request,
                "secret_key": secret_key,
                "error": error,
                "success_message": "",
                "priority_options": emails_options,
            },
        )

    # Create a new EmailSubmission record
    email_submission = EmailSubmission(
        username=user,
        from_field=from_field,
        to_field=to_field,
        subject=subject,
        html_content=html_content,
    )
    db.add(email_submission)
    db.commit()
    db.refresh(email_submission)

    # Prepare data to send to external URL
    post_data = {
        "from": f"{user} <{from_field}>",
        "to": to_field,
        "subject": subject,
        "html": html_content,
    }
    if not secret_key:
        secret_key = (
            db.query(Role)
            .filter(
                and_(
                    Role.role == current_user.get("role", "guise"),
                    Role.email == selected_suffix,
                )
            )
            .first()
            .key
        )
    # logging.info(f"Secret key: {secret_key}")
    try:
        domin = from_field.split("@")[1]
        response = post_email(post_data, domin, secret_key)
        response.raise_for_status()
        external_response = response.text
    except requests.RequestException as e:
        error = f"Failed to send POST request: {e}"
        return templates.TemplateResponse(
            "send_email.html",
            {
                "request": request,
                "secret_key": secret_key,
                "error": error,
                "success_message": "",
                "priority_options": emails_options,
            },
        )

    # Render the response from external URL
    return templates.TemplateResponse(
        "send_email.html",
        {
            "request": request,
            "secret_key": secret_key,
            "error": "",
            "success_message": "Email submitted successfully!",
            "priority_options": emails_options,
            "external_response": external_response,
        },
    )


@app.post("/receive/mime")
async def receive_mailgun_webhook(
    request: Request,  # 捕获整个请求体
    recipient: str = Form(...),
    sender: str = Form(...),
    from_header: str = Form(..., alias="from"),
    subject: str = Form(...),
    body_plain: Optional[str] = Form(None, alias="body-mime"),
    timestamp: str = Form(...),
    token: str = Form(...),
    signature: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    接收 Mailgun 的 POST 请求，并解析所有字段。
    """
    # 捕获并打印完整的请求数据
    try:
        logging.info(f"Recipient: {recipient}")
        logging.info(f"Sender: {sender}")
        logging.info(f"From Header: {from_header}")
        logging.info(f"Subject: {subject}")
        # logging.info(f"Body Plain: {body_plain}")
        logging.info(f"Timestamp: {timestamp}")
        logging.info(f"Token: {token}")
        logging.info(f"Signature: {signature}")
        try:

            # 解析邮件正文
            # 使用 email 模块解析 MIME 数据
            msg = email.message_from_string(body_plain, policy=policy.default)
            # 提取所有正文内容
            data_user = {"from": from_header, "subject": subject}

            body_parts = extract_body_recursive(msg)
            rec = recipient.split(",")[0]
            for i in body_parts:
                data_user[i[0]] = i[1]
            logging.info(f"Body parts: {data_user}")
        except Exception as e:
            logging.error(f"Error extracting body parts: {str(e)}")
            raise HTTPException(
                status_code=400, detail="Failed to extract body parts from MIME data"
            )
        write_email_to_db(rec, data_user, db)
        return {
            "recipient": recipient,
            "sender": sender,
            "from_header": from_header,
            "subject": subject,
            "body_plain": body_plain,
            "timestamp": timestamp,
            "token": token,
            "signature": signature,
        }

    except Exception as e:
        logging.error(f"Error processing Mailgun webhook: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to process Mailgun webhook")


@app.post("/opaochat/recive")
async def receive_mailgun_forward(
    request: Request,  # 捕获整个请求体
    db: Session = Depends(get_db),
):
    """
    接收 Mailgun 的 POST 请求，并解析所有字段。
    """
    try:
        # 捕获并打印完整的请求数据
        raw_data = await request.body()
        # 将字节数据解码为字符串
        raw_text = raw_data.decode("utf-8")
        # 将字符串解析为 JSON 对象
        parsed_data = json.loads(raw_text)
        rec = parsed_data.get("recipients")[0]
        logging.info(rec)
        text = parsed_data.get("text", "")
        html = parsed_data.get("html", "")
        from_header = parsed_data["from"]["value"][0]
        from_user = f"{from_header['name']} <{from_header['address']}>"

        data_user = {
            "from": from_user,
            "subject": "接收专用",
            "text/plain": text,
            "text/html": html,
        }
        write_email_to_db(rec, data_user, db)
        logging.info(data_user)

    except Exception as e:
        logging.error(e)
    return {
        "message": "Mailgun webhook received",
    }


if __name__ == "__main__":

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
