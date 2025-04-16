#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EmailForward - 域名邮箱系统
一个功能强大的自定义域名邮箱管理系统，支持多域名收发邮件、用户管理和API访问。
"""

# 标准库导入
from datetime import datetime, timedelta, timezone
import hashlib
import json
import logging
import re
from math import ceil
from typing import Optional, Dict, List, Any

# 第三方库导入
import httpx
import jwt
import requests
import uvicorn
from cachetools import TTLCache
from fastapi import (
    FastAPI, Request, Form, HTTPException, Depends, 
    status, Query, Response
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
import email
from email import policy

# 本地导入
from models import User, Record, Role, EmailSubmission
from database import get_db
import config

# ===============================
# 配置日志
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# ===============================
# 全局变量
# ===============================
# 从配置中获取验证码邮箱域名
code_email = config.code_email

# 创建全局缓存对象：最大容量为100，过期时间为300秒（5分钟）
global_cache = TTLCache(maxsize=100, ttl=300)

# ===============================
# 应用初始化
# ===============================
# 导入数据库初始化函数
from init_db import init_db as initialize_database

app = FastAPI(
    title="EmailForward",
    description="一个功能强大的自定义域名邮箱管理系统",
    version="1.0.0",
    docs_url=None,  # 关闭自动生成的API文档
    redoc_url=None,
    openapi_url=None
)

# 自动初始化数据库
logger.info("Checking database...")
if initialize_database():
    logger.info("Database check completed.")
else:
    logger.error("Database check failed! Application may not function correctly.")

# 跨域中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化模板
templates = Jinja2Templates(directory="templates")

# ===============================
# 工具函数
# ===============================

# 缓存相关函数
async def set_variable(key: str, value: Any) -> None:
    """
    设置一个全局变量，自动过期
    
    Args:
        key: 变量名
        value: 变量值
    """
    global_cache[key] = value

async def get_variable(key: str) -> Optional[Any]:
    """
    获取全局变量值，如果不存在或已过期返回 None
    
    Args:
        key: 变量名
    
    Returns:
        变量值或None
    """
    return global_cache.get(key)

# 身份验证相关函数
def hash_password(password: str) -> str:
    """
    对密码进行哈希处理
    
    Args:
        password: 原始密码
    
    Returns:
        哈希后的密码
    """
    return hashlib.sha256(password.encode()).hexdigest()

async def create_access_token(data: Dict[str, Any], expire: timedelta) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码的数据
        expire: 过期时间
    
    Returns:
        编码后的JWT令牌
    """
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.secret_key, algorithm=config.algorithms)

def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """
    验证用户凭据
    
    Args:
        username: 用户名
        password: 密码
        db: 数据库会话
    
    Returns:
        如果验证成功，返回用户对象；否则返回None
    """
    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名或密码不能为空")
    
    user = db.query(User).filter(User.username == username).first()
    if user and user.password == hash_password(password):
        return user
    return None

# 邮件处理相关函数
def post_email(data: Dict[str, Any], domain: str, api: str) -> requests.Response:
    """
    通过Mailgun API发送电子邮件
    
    Args:
        data: 电子邮件数据
        domain: 发送域名
        api: Mailgun API密钥
    
    Returns:
        API响应对象
    """
    to_data = data.get("to", "")
    data["to"] = [email.strip() for email in to_data.split(",")]

    url = f"https://api.mailgun.net/v3/{domain}/messages"
    return requests.post(
        url,
        auth=("api", api),
        data=data,
    )

def extract_body_recursive(message) -> List[tuple]:
    """
    递归提取电子邮件正文
    
    Args:
        message: 电子邮件消息对象
    
    Returns:
        包含内容类型和正文的元组列表
    """
    parts = []
    if message.is_multipart():
        # 遍历多部分邮件
        for part in message.iter_parts():
            parts.extend(extract_body_recursive(part))
    else:
        # 处理单个部分
        content_type = message.get_content_type()
        charset = message.get_content_charset() or "utf-8"
        try:
            payload = message.get_payload(decode=True)
            if payload:
                parts.append((content_type, payload.decode(charset)))
        except (UnicodeDecodeError, AttributeError):
            parts.append(
                (content_type, f"Error decoding content with charset {charset}")
            )
    return parts

def write_email_to_db(username: str, data: Dict[str, str], db: Session) -> Record:
    """
    将电子邮件数据写入数据库
    
    Args:
        username: 电子邮件用户名
        data: 电子邮件数据
        db: 数据库会话
    
    Returns:
        创建的Record对象
    """
    username_parts = username.split("@")
    record = Record(
        email_user=username_parts[0],
        email_domain=username_parts[-1],
        subject=data.get("subject", ""),
        from_field=data.get("from", ""),
        text_plain=data.get("text/plain", ""),
        text_html=data.get("text/html", ""),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

# ===============================
# 依赖项
# ===============================

# 获取当前用户
async def get_current_user(request: Request) -> Dict[str, str]:
    """
    从请求中获取当前登录用户信息
    
    Args:
        request: 请求对象
    
    Returns:
        包含用户信息的字典
    
    Raises:
        RedirectToLoginException: 如果用户未登录或会话已过期
    """
    token = request.cookies.get("access_token")
    if not token:
        raise RedirectToLoginException()
    
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithms])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if not username or not role:
            raise RedirectToLoginException()
            
        return {"username": username, "role": role}
    except:
        raise RedirectToLoginException()

# API密钥验证依赖项
security_bearer = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    api_key: Optional[str] = Depends(api_key_header),
) -> str:
    """
    从请求中获取API密钥
    
    Args:
        authorization: 授权凭据
        api_key: API密钥
    
    Returns:
        API密钥字符串
    
    Raises:
        HTTPException: 如果未提供有效的API密钥
    """
    if authorization and authorization.scheme == "Bearer":
        return authorization.credentials
    if api_key:
        return api_key
    raise HTTPException(status_code=403, detail="Could not validate API key")

async def get_optional_key(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    api_key: Optional[str] = Depends(api_key_header),
) -> Optional[str]:
    """
    从请求中获取可选的API密钥
    
    Args:
        authorization: 授权凭据
        api_key: API密钥
    
    Returns:
        API密钥字符串，如果未提供则返回None
    """
    if authorization and authorization.scheme == "Bearer":
        return authorization.credentials
    if api_key:
        return api_key
    return None

# ===============================
# 自定义异常
# ===============================
class RedirectToLoginException(Exception):
    """重定向到登录页面的异常"""
    def __init__(self, redirect_url: str = "/login"):
        self.redirect_url = redirect_url

# ===============================
# 异常处理器
# ===============================
@app.exception_handler(RedirectToLoginException)
async def redirect_to_login_handler(request: Request, exc: RedirectToLoginException):
    """处理重定向到登录页面的异常"""
    return RedirectResponse(url=exc.redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """处理HTTP异常"""
    logger.error(f"HTTP Exception: {exc}")
    return RedirectResponse(url="/404")

# ===============================
# 基本路由
# ===============================
@app.get("/404", response_class=HTMLResponse)
async def not_found(request: Request):
    """404页面"""
    return templates.TemplateResponse("404.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request, 
    user=Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    主页路由
    
    Args:
        request: 请求对象
        user: 当前用户
        db: 数据库会话
    
    Returns:
        HTML响应
    """
    if not user:
        raise RedirectToLoginException()
    
    # 获取完整的用户信息，包括密钥
    user_data = db.query(User).filter(User.username == user.get("username")).first()
    
    # 创建包含完整用户信息的字典
    user_info = {
        "username": user.get("username"),
        "role": user.get("role"),
        "key": user_data.key if user_data else ""
    }
    
    emails = db.query(Role).filter(Role.role == user.get("role", "guise")).all()
    emails_options = [email.email.replace("@", "") for email in emails if emails]
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user_info,
            "username": "",
            "emails_options": emails_options,
            "code": "\n".join(emails_options),
        },
    )

# ===============================
# 认证路由
# ===============================
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    """登录页面(GET)"""
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": None,
            "turnstile_site_key": config.turnstile_site_key,
        },
    )

@app.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    处理登录(POST)
    
    Args:
        request: 请求对象
        username: 用户名
        password: 密码
        db: 数据库会话
    
    Returns:
        登录成功时重定向到主页，否则返回登录页面并显示错误
    """
    # 验证Cloudflare Turnstile (如果配置了)
    if config.turnstile_site_key and config.turnstile_secret_key:
        turnstile_token = (await request.form()).get("cf-turnstile-response")
        if turnstile_token:
            # 验证Turnstile令牌
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                    data={
                        "secret": config.turnstile_secret_key,
                        "response": turnstile_token,
                        "remoteip": request.client.host,
                    },
                )
            result = resp.json()

            if not result.get("success"):
                # 验证失败处理
                error = "Turnstile verification failed. Please try again."
                return templates.TemplateResponse(
                    "login.html",
                    {
                        "request": request,
                        "error": error,
                        "turnstile_site_key": config.turnstile_site_key,
                    },
                )

    # 验证用户
    user = authenticate_user(username, password, db)
    logger.info(f"User login attempt: {username}")
    
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "用户名或密码错误",
                "turnstile_site_key": config.turnstile_site_key,
            },
        )
    
    # 创建JWT访问令牌
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=config.access_token_expire_minutes
    )
    access_token = await create_access_token(
        data={"sub": user.username, "role": user.role},
        expire=expires,
    )
    
    # 设置Cookie并重定向
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=config.access_token_expire_minutes * 60,
    )
    return response

@app.get("/logout")
async def logout_get(request: Request, response: Response):
    """
    用户注销(GET方法)
    
    Args:
        request: 请求对象
        response: 响应对象
    
    Returns:
        重定向到登录页面
    """
    # 为了向后兼容，保留GET方法的登出功能，但使用更彻底的cookie清除方法
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # 清除所有可能的cookie变体，包括不同的路径和安全设置
    response.delete_cookie("access_token")
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("access_token", path="/", secure=True)
    response.delete_cookie("access_token", path="/", secure=True, samesite="None")
    response.delete_cookie("access_token", path="/", secure=True, samesite="Lax")
    response.delete_cookie("access_token", path="/", secure=True, samesite="Strict")
    response.delete_cookie("access_token", path="/", httponly=True)
    
    # 通过设置过期时间为过去的时间来确保cookie被删除
    expired_time = datetime.now(timezone.utc) - timedelta(days=1)
    response.set_cookie(
        key="access_token",
        value="",
        expires=expired_time.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        httponly=True,
        path="/",
    )
    
    logger.info("User logged out via GET method")
    return response

@app.post("/logout")
async def logout_post(request: Request):
    """
    用户注销(POST方法)
    
    Args:
        request: 请求对象
    
    Returns:
        重定向到登录页面
    """
    # 创建响应对象
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # 清除所有可能的cookie变体，包括不同的路径和安全设置
    response.delete_cookie("access_token")
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("access_token", path="/", secure=True)
    response.delete_cookie("access_token", path="/", secure=True, samesite="None")
    response.delete_cookie("access_token", path="/", secure=True, samesite="Lax")
    response.delete_cookie("access_token", path="/", secure=True, samesite="Strict")
    response.delete_cookie("access_token", path="/", httponly=True)
    
    # 通过设置过期时间为过去的时间来确保cookie被删除
    expired_time = datetime.now(timezone.utc) - timedelta(days=1)
    response.set_cookie(
        key="access_token",
        value="",
        expires=expired_time.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        httponly=True,
        path="/",
    )
    
    logger.info("User logged out via POST method")
    return response

# ===============================
# 邮件查询路由
# ===============================
@app.post("/search", response_class=HTMLResponse)
def search_user(
    request: Request,
    username: str = Form(...),
    emails: str = Form(...),
    currentuser=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    处理搜索表单提交并显示用户数据
    
    Args:
        request: 请求对象
        username: 邮箱用户名部分
        emails: 邮箱域名部分
        currentuser: 当前登录用户
        db: 数据库会话
    
    Returns:
        HTML响应
    """
    if not currentuser:
        raise RedirectToLoginException()
    
    email_user = username.strip().lower()
    email_domain = emails.strip()

    # 查询可用的邮箱域名
    emails = db.query(Role).filter(Role.role == currentuser.get("role", "guise")).all()
    emails_options = [email.email.replace("@", "") for email in emails if emails]

    # 查询用户邮件记录(过去24小时内)
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
    显示特定记录的文本/纯文本和文本/HTML
    
    Args:
        request: 请求对象
        record_id: 记录ID
        email_domin: 电子邮件域名
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        HTML响应
    """
    if not current_user:
        raise RedirectToLoginException()
    
    # 获取电子邮件用户和域名
    email_data = email_domin.strip().split("@")
    if len(email_data) != 2:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # 查询记录
    record = (
        db.query(Record)
        .filter(
            and_(
                Record.id == record_id,
                Record.email_user == email_data[0],
                Record.email_domain == email_data[1],
            )
        )
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")

    # 连接text/plain和text/html
    concatenated_content = f"<p>{record.text_plain}</p>\n{record.text_html}"
    subject = record.subject
    
    return templates.TemplateResponse(
        "display_record.html",
        {"request": request, "content": concatenated_content, "subject": subject},
    )

@app.get("/resend/{send_id}", response_class=HTMLResponse)
def resend_email(
    request: Request,
    send_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    重新发送电子邮件提交
    
    Args:
        request: 请求对象
        send_id: 发送ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        HTML响应
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

# ===============================
# 管理员路由
# ===============================
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, user: User = Depends(get_current_user)):
    """
    管理员页面 - 重定向到all用户页面
    
    Args:
        request: 请求对象
        user: 当前用户
    
    Returns:
        重定向到all页面
    """
    if not user or user.get("role", "") != "admin":
        return RedirectResponse(url="/")
    
    # 重定向到all页面，并设置action=users以显示用户管理界面
    return RedirectResponse(url="/all?action=users", status_code=status.HTTP_303_SEE_OTHER)

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
    """
    创建新用户
    
    Args:
        request: 请求对象
        username: 用户名
        password: 密码
        role: 角色
        key: 密钥
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        HTML响应
    """
    if not current_user or current_user.get("role", "") != "admin":
        return RedirectResponse(url="/")
    
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return RedirectResponse(
            url="/all?action=users&user_creation_error=用户名已存在", 
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 哈希密码并创建新用户
    hashed_password = hash_password(password)
    new_user = User(username=username, password=hashed_password, role=role, key=key)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(
        url="/all?action=users&user_creation_success=true", 
        status_code=status.HTTP_303_SEE_OTHER
    )

@app.post("/admin/create_role", response_class=HTMLResponse)
async def create_role(
    request: Request,
    role: str = Form(...),
    email: str = Form(...),
    key: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建新角色
    
    Args:
        request: 请求对象
        role: 角色名称
        email: 电子邮件域名
        key: 密钥
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        HTML响应
    """
    if not current_user or current_user.get("role", "") != "admin":
        return RedirectResponse(url="/")

    # 确保电子邮件格式正确
    email_clean = email.strip()
    if not email_clean.startswith('@'):
        email_clean = '@' + email_clean
        
    # 创建新角色
    new_role = Role(role=role, email=email_clean, key=key)
    db.add(new_role)
    try:
        db.commit()
        db.refresh(new_role)
    except IntegrityError:
        db.rollback()
        return RedirectResponse(
            url="/all?action=users&role_creation_error=在该角色下，该邮箱已存在",
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url="/all?action=users&role_creation_success=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

@app.delete("/delete_role/{roleId}", response_class=HTMLResponse)
async def delete_role(
    request: Request,
    roleId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除角色
    
    Args:
        request: 请求对象
        roleId: 角色ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        重定向响应
    """
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
    """
    更新用户信息
    
    Args:
        request: 请求对象
        user_id: 用户ID
        username: 用户名
        role: 角色
        password: 密码(可选)
        key: 密钥(可选)
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        重定向响应
    """
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
    """
    更新角色信息
    
    Args:
        request: 请求对象
        role_id: 角色ID
        role_name: 角色名称
        email: 电子邮件域名
        key: 密钥(可选)
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        重定向响应
    """
    if not current_user or current_user.get("role", "") != "admin":
        return RedirectResponse(url="/")
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        return RedirectResponse(url="/404", status_code=status.HTTP_303_SEE_OTHER)
    
    # 确保电子邮件格式正确
    email_clean = email.strip()
    if not email_clean.startswith('@'):
        email_clean = '@' + email_clean
        
    role.role = role_name
    role.email = email_clean
    if key:
        role.key = key

    try:
        db.commit()
        db.refresh(role)
    except IntegrityError:
        db.rollback()
        logger.error(f"IntegrityError updating role {role_id}")
        return RedirectResponse(url="/all?error=duplicate_role_email", status_code=status.HTTP_303_SEE_OTHER)
    
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
    error: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    管理员查询页面，可查看所有用户、角色、记录和发送邮件的记录
    
    Args:
        request: 请求对象
        action: 操作类型
        user_page: 用户页码
        role_page: 角色页码
        record_page: 记录页码
        record_domain: 记录域名
        send_page: 发送页码
        send_total_pages: 发送总页数
        username: 用户名
        error: 错误消息
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        HTML响应
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
    
    # 分别根据action类型查询不同的数据
    if action == "users":
        # 查询所有用户
        users = db.query(User).offset((user_page - 1) * 10).limit(10).all()
        total_records = db.query(User).count()
        user_total_pages = ceil(total_records / 10)

    elif action == "roles":
        # 查询所有角色
        roles = db.query(Role).offset((role_page - 1) * 10).limit(10).all()
        total_records = db.query(Role).count()
        role_total_pages = ceil(total_records / 10)

    elif action == "records":
        # 查询所有记录
        records_query = db.query(Record)
        if record_domain:
            records_query = records_query.filter(
                Record.email_domain == record_domain.strip()
            )
        total_records = records_query.count()
        record_total_pages = ceil(total_records / 10)
        records = (
            records_query.order_by(desc(Record.id))
            .offset((record_page - 1) * 10)
            .limit(10)
            .all()
        )

    elif action == "sendemail":
        # 查询所有发送的邮件
        send_query = db.query(EmailSubmission)
        if username:
            send_query = send_query.filter(EmailSubmission.username == username.strip())
        total_records = send_query.count()
        send_total_pages = ceil(total_records / 10)
        sends = (
            send_query.order_by(desc(EmailSubmission.id))
            .offset((send_page - 1) * 10)
            .limit(10)
            .all()
        )

    return templates.TemplateResponse(
        "all_users.html",
        {
            "request": request,
            "user": current_user,  # 确保正确传递用户信息到模板
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
            "error": error
        },
    )

# ===============================
# 邮件发送路由
# ===============================
@app.get("/send-email", response_class=HTMLResponse)
def send_email_form(
    request: Request, 
    user=Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    显示邮件发送表单
    
    Args:
        request: 请求对象
        user: 当前用户
        db: 数据库会话
    
    Returns:
        HTML响应
    """
    if not user:
        raise RedirectToLoginException()
    
    # 查询用户可用的邮箱域名
    emails = db.query(Role).filter(Role.role == user.get("role", "guise")).all()
    emails_options = [
        email.email for email in emails if emails and email.email.startswith("@")
    ]

    return templates.TemplateResponse(
        "send_email.html",
        {
            "request": request,
            "user": user,  # 确保传递 user 变量到模板
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
    处理邮件发送表单
    
    Args:
        request: 请求对象
        secret_key: 密钥(可选)
        username: 用户名
        priority: 优先级
        to_field: 收件人
        subject: 主题
        html_content: HTML内容
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        HTML响应
    """
    if not current_user:
        raise RedirectToLoginException()
    
    username = username.strip().lower()
    selected_suffix = priority.strip()
    from_field = f"{username}{selected_suffix}"
    user = current_user.get("username", "")

    # 查询用户可用的邮箱域名
    emails = db.query(Role).filter(Role.role == current_user.get("role", "guise")).all()
    emails_options = [
        email.email for email in emails if emails and email.email.startswith("@")
    ]

    # 验证所有字段都提供了
    if not all([username, to_field, subject, html_content]):
        error = "All fields are required."
        return templates.TemplateResponse(
            "send_email.html",
            {
                "request": request,
                "user": current_user,  # 确保传递 user 变量到模板
                "secret_key": secret_key,
                "error": error,
                "success_message": "",
                "priority_options": emails_options,
            },
        )

    # 创建新的邮件发送记录
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

    # 准备要发送到外部URL的数据
    post_data = {
        "from": f"{user} <{from_field}>",
        "to": to_field,
        "subject": subject,
        "html": html_content,
    }
    
    # 如果没有提供密钥，则从角色表中获取
    if not secret_key:
        role_with_key = (
            db.query(Role)
            .filter(
                and_(
                    Role.role == current_user.get("role", "guise"),
                    Role.email == selected_suffix,
                )
            )
            .first()
        )
        
        if not role_with_key:
            error = f"未找到与域名 {selected_suffix} 匹配的密钥"
            return templates.TemplateResponse(
                "send_email.html",
                {
                    "request": request,
                    "user": current_user,  # 确保传递 user 变量到模板
                    "secret_key": secret_key,
                    "error": error,
                    "success_message": "",
                    "priority_options": emails_options,
                },
            )
        
        secret_key = role_with_key.key
    
    try:
        # 解析域名
        if "@" not in from_field:
            error = f"无效的邮件地址: {from_field}"
            return templates.TemplateResponse(
                "send_email.html",
                {
                    "request": request,
                    "user": current_user,  # 确保传递 user 变量到模板
                    "secret_key": secret_key,
                    "error": error,
                    "success_message": "",
                    "priority_options": emails_options,
                },
            )
            
        domain = from_field.split("@")[1]
        
        # 发送邮件
        response = post_email(post_data, domain, secret_key)
        response.raise_for_status()
        external_response = response.text
    except requests.RequestException as e:
        error = f"Failed to send POST request: {e}"
        return templates.TemplateResponse(
            "send_email.html",
            {
                "request": request,
                "user": current_user,  # 确保传递 user 变量到模板
                "secret_key": secret_key,
                "error": error,
                "success_message": "",
                "priority_options": emails_options,
            },
        )

    # 呈现来自外部URL的响应
    return templates.TemplateResponse(
        "send_email.html",
        {
            "request": request,
            "user": current_user,  # 确保传递 user 变量到模板
            "secret_key": secret_key,
            "error": "",
            "success_message": "Email submitted successfully!",
            "priority_options": emails_options,
            "external_response": external_response,
        },
    )

# ===============================
# Webhook接收邮件路由
# ===============================
@app.post("/receive/mime")
async def receive_mailgun_webhook(
    request: Request,
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
    接收Mailgun的POST请求，并解析所有字段
    
    Args:
        request: 请求对象
        recipient: 收件人
        sender: 发件人
        from_header: From头
        subject: 主题
        body_plain: MIME正文
        timestamp: 时间戳
        token: 令牌
        signature: 签名
        db: 数据库会话
    
    Returns:
        处理结果
    """
    try:
        logger.info(f"Recipient: {recipient}")
        logger.info(f"Sender: {sender}")
        logger.info(f"From Header: {from_header}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Timestamp: {timestamp}")
        logger.info(f"Token: {token}")
        logger.info(f"Signature: {signature}")
        
        try:
            # 解析邮件正文
            msg = email.message_from_string(body_plain, policy=policy.default)
            data_user = {"from": from_header, "subject": subject}

            body_parts = extract_body_recursive(msg)
            rec = recipient.split(",")[0]
            for i in body_parts:
                data_user[i[0]] = i[1]
            logger.info(f"Body parts: {len(body_parts)}")
        except Exception as e:
            logger.error(f"Error extracting body parts: {str(e)}")
            raise HTTPException(
                status_code=400, detail="Failed to extract body parts from MIME data"
            )
        
        # 将邮件写入数据库
        write_email_to_db(rec, data_user, db)
        
        return {
            "status": "success",
            "message": "Email received and processed successfully",
        }

    except Exception as e:
        logger.error(f"Error processing Mailgun webhook: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to process Mailgun webhook")

@app.post("/opaochat/recive")
async def receive_mailgun_forward(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    接收Mailgun的POST请求(转发)，并解析所有字段
    
    Args:
        request: 请求对象
        db: 数据库会话
    
    Returns:
        处理结果
    """
    try:
        # 获取并解析请求数据
        raw_data = await request.body()
        raw_text = raw_data.decode("utf-8")
        parsed_data = json.loads(raw_text)
        
        # 提取必要的字段
        recipients = parsed_data.get("recipients", [])
        if not recipients:
            return {"message": "No recipients found", "status": "error"}
            
        rec = recipients[0]
        logger.info(f"Recipient: {rec}")
        
        text = parsed_data.get("text", "")
        html = parsed_data.get("html", "")
        
        # 确保from字段存在并有值
        if "from" not in parsed_data or "value" not in parsed_data["from"] or not parsed_data["from"]["value"]:
            from_user = "Unknown Sender <unknown@example.com>"
        else:
            from_header = parsed_data["from"]["value"][0]
            name = from_header.get('name', 'Unknown')
            address = from_header.get('address', 'unknown@example.com')
            from_user = f"{name} <{address}>"

        data_user = {
            "from": from_user,
            "subject": parsed_data.get("subject", "接收专用"),
            "text/plain": text,
            "text/html": html,
        }
        
        # 将邮件写入数据库
        write_email_to_db(rec, data_user, db)
        
        return {
            "message": "Mailgun webhook received and processed",
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Error processing Mailgun forward: {str(e)}")
        return {
            "message": f"Error processing request: {str(e)}",
            "status": "error"
        }

# ===============================
# OpenAPI路由
# ===============================
@app.post("/openapi/record/emails")
async def get_emails(
    request: Request,
    api_key=Depends(get_api_key),
    db: Session = Depends(get_db),
):
    """
    查询邮件记录的API接口
    
    Args:
        request: 请求对象
        api_key: API密钥
        db: 数据库会话
    
    Returns:
        包含邮件记录的JSON响应
    """
    try:
        body = await request.json()
    except:
        return {"message": "Invalid JSON body", "status": "error"}
        
    username = body.get("username", "").strip()
    email_user = body.get("email_user", "").strip()
    email_domain = body.get("email_domain", "").strip()
    num = int(body.get("num", 1))
    
    if not username or not email_domain or not api_key:
        return {"message": "username and email_domain must not be empty", "status": "error"}

    # 查询用户key对应的权限
    emails_options = await get_variable(f"{username}:{api_key}")

    if not emails_options:  # 如果缓存中没有数据
        user = (
            db.query(User)
            .filter(and_(User.username == username, User.key == api_key))
            .first()
        )
        if not user:
            return {"message": "API key is invalid", "status": "error"}
            
        emails = db.query(Role).filter(Role.role == user.role).all()
        emails_options = [email.email.replace("@", "") for email in emails if emails]
        
        # 设置缓存
        await set_variable(f"{username}:{api_key}", emails_options)
        
    if not emails_options or email_domain not in emails_options:
        return {"message": "email_domain is invalid or not allowed", "status": "error"}
        
    # 查询用户的邮件记录
    records_query = db.query(Record).filter(Record.email_domain == email_domain)
    if email_user:
        records_query = records_query.filter(Record.email_user == email_user)
        
    records = records_query.order_by(desc(Record.id)).limit(num).all()
    
    # 将记录转换为可JSON序列化的对象
    result = []
    for record in records:
        result.append({
            "id": record.id,
            "email_user": record.email_user,
            "email_domain": record.email_domain,
            "from_field": record.from_field,
            "subject": record.subject,
            "text_plain": record.text_plain,
            "text_html": record.text_html,
            "created_at": record.created_at.isoformat() if record.created_at else None
        })

    return {"records": result, "status": "success"}

@app.get("/openapi/record/code/{username}")
async def get_code(
    username: str,
    key: Optional[str] = None,
    api_key=Depends(get_optional_key),
    db: Session = Depends(get_db),
):
    """
    提取验证码的API接口
    
    Args:
        username: 用户名
        key: 密钥(可选)
        api_key: API密钥
        db: 数据库会话
    
    Returns:
        验证码或错误消息
    """
    if not api_key and not key:
        return {"message": "API key is required", "status": "error"}
        
    if not username:
        return {"message": "username must not be empty", "status": "error"}
        
    if not code_email:
        return {"message": "code_email is not configured", "status": "error"}
        
    if not api_key:
        api_key = key

    # 验证API密钥
    emails_options = await get_variable(f"{username}:{api_key}")

    if not emails_options:  # 如果缓存中没有数据
        user = db.query(User).filter(User.key == api_key).first()
        if not user:
            return {"message": "API key is invalid", "status": "error"}
            
        # 设置缓存
        await set_variable(f"{username}:{api_key}", "email")

    # 查询最新的验证码邮件
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    record = (
        db.query(Record)
        .filter(
            and_(
                Record.email_user == username,
                Record.email_domain == code_email,
                Record.created_at >= one_day_ago,
            )
        )
        .order_by(desc(Record.id))
        .first()
    )
    
    if not record:
        return {"message": "没有找到验证码邮件", "status": "error"}
        
    # 使用正则表达式提取验证码
    pattern = re.compile(
        r"(?i)(?:验证码|驗證碼|captcha|code|verify|check|auth|token|pw|pass|password|verification)\s*[:：]?\s*([A-Za-z0-9]{4,20})"
    )
    content = f"<p>{record.text_plain}</p>\n{record.text_html}"
    match = pattern.search(content)
    
    if match:
        return {"code": match.group(1), "status": "success"}
        
    return {"message": "没有提取到验证码，请手动去邮箱查看", "status": "error"}

# ===============================
# 密钥重置路由
# ===============================
@app.post("/reset_key")
async def reset_key(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Dict[str, str] = Depends(get_current_user),
):
    """
    重置用户API密钥
    
    Args:
        request: 请求对象
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        重定向回首页，显示密钥重置成功消息
    """
    if not current_user:
        raise RedirectToLoginException()
    
    # 获取用户信息
    username = current_user.get("username")
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 生成新的随机密钥
    import secrets
    import string
    
    # 生成36位随机字符的密钥
    alphabet = string.ascii_letters + string.digits
    new_key = ''.join(secrets.choice(alphabet) for _ in range(36))
    
    # 更新用户密钥
    user.key = new_key
    db.commit()
    
    # 重定向回首页，带上成功消息
    response = RedirectResponse(url="/?success_message=API密钥已成功重置", status_code=status.HTTP_303_SEE_OTHER)
    return response

# ===============================
# 用户功能路由
# ===============================
@app.post("/change-password", response_class=HTMLResponse)
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: Dict[str, str] = Depends(get_current_user),
):
    """
    处理密码修改
    
    Args:
        request: 请求对象
        current_password: 当前密码
        new_password: 新密码
        confirm_password: 确认新密码
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        HTML响应
    """
    if not current_user:
        raise RedirectToLoginException()
    
    # 验证新密码和确认密码是否一致
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "user": current_user,
                "username": "",
                "emails_options": [],
                "code": "",
                "error_message": "新密码与确认密码不一致，请重新输入！",
            },
        )
    
    # 获取用户数据
    user = db.query(User).filter(User.username == current_user.get("username")).first()
    if not user:
        logger.error(f"无法找到用户: {current_user.get('username')}")
        raise RedirectToLoginException()
    
    # 验证当前密码
    hashed_current_password = hash_password(current_password)
    if user.password != hashed_current_password:
        emails = db.query(Role).filter(Role.role == current_user.get("role", "guise")).all()
        emails_options = [email.email.replace("@", "") for email in emails if emails]
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "user": current_user,
                "username": "",
                "emails_options": emails_options,
                "code": "\n".join(emails_options),
                "error_message": "当前密码错误，密码修改失败！",
            },
        )
    
    # 更新密码
    user.password = hash_password(new_password)
    try:
        db.commit()
        db.refresh(user)
        
        emails = db.query(Role).filter(Role.role == current_user.get("role", "guise")).all()
        emails_options = [email.email.replace("@", "") for email in emails if emails]
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "user": current_user,
                "username": "",
                "emails_options": emails_options,
                "code": "\n".join(emails_options),
                "success_message": "密码修改成功！",
            },
        )
    except Exception as e:
        logger.error(f"密码修改错误: {e}")
        
        emails = db.query(Role).filter(Role.role == current_user.get("role", "guise")).all()
        emails_options = [email.email.replace("@", "") for email in emails if emails]
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "user": current_user,
                "username": "",
                "emails_options": emails_options,
                "code": "\n".join(emails_options),
                "error_message": f"密码修改失败: {str(e)}",
            },
        )

@app.post("/reset_key", response_class=HTMLResponse)
async def reset_key(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    重置用户API密钥
    
    Args:
        request: 请求对象
        user: 当前用户
        db: 数据库会话
    
    Returns:
        重定向到首页
    """
    if not user:
        raise RedirectToLoginException()
    
    username = user.get("username")
    
    # 获取用户记录
    user_record = db.query(User).filter(User.username == username).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 生成新的密钥
    new_key = hashlib.sha256(f"{username}:{datetime.now()}".encode()).hexdigest()
    
    # 更新用户记录
    user_record.key = new_key
    db.commit()
    
    # 重定向到首页
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.delete("/delete_user/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除用户
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        JSON响应
    """
    # 验证当前用户是否为管理员
    if not current_user or current_user.get("role", "") != "admin":
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "无权限执行此操作"}
        )

    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "用户不存在"}
        )

    # 不允许删除管理员用户
    if user.role == "admin" and user.username != current_user.get("username"):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "不能删除其他管理员用户"}
        )
    # 不允许删除自己
    if user.username == current_user.get("username"):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "不能删除自己"}
        )
    # 删除用户
    db.delete(user)
    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "用户删除成功"}
    )

# ===============================
# 主入口
# ===============================
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
