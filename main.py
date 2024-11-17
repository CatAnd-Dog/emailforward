
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
import logging
import json

import os

adminkey = os.getenv("KEY","")
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # 日志输出到控制台
    ],
)
app = FastAPI(docs_url=None,  # 禁用 Swagger UI
    redoc_url=None,  # 禁用 ReDoc
    openapi_url=None  # 禁用 OpenAPI 文档
    )

@app.get("/")
async def receive():

    return {
            "message": "powwered by opao",
        }

data_global = {}


@app.post("/email")
async def receive_mailgun_webhook(
    request: Request,  # 捕获整个请求体
):
    """
    接收 Mailgun 的 POST 请求，并解析所有字段。
    """
    logging.info(request)
    try:
        # 捕获并打印完整的请求数据
        raw_data = await request.body()
        # 将字节数据解码为字符串
        raw_text = raw_data.decode("utf-8")
        # 将字符串解析为 JSON 对象
        parsed_data = json.loads(raw_text)
        rec = parsed_data.get("recipients")[0].split("@")[0]
        logging.info(rec)
        text = parsed_data.get("text", "")
        html = parsed_data.get("html", "")
        textAsHtml = parsed_data.get("textAsHtml ", "")
        data_global[rec] = {
            "text": text,
            "html": html,
            "textAsHtml": textAsHtml,
        }
        logging.info(data_global[rec])

    except Exception as e:
        logging.error(e)
    return {
            "message": "Mailgun webhook received",
        }

# 查询所有数据
@app.get("/data/admin")
async def admin_all(
    key: str = Query(None),
):
    if not adminkey or key != adminkey:
         raise HTTPException(status_code=400, detail="Key is incorrect")
    
    global data_global  
    return data_global

# 删除所有数据
@app.delete("/data/admin")
async def admin_all_delete(
    key: str = Query(None),
):
    if not adminkey or key != adminkey:
         raise HTTPException(status_code=400, detail="Key is incorrect")
    
    global data_global  
    data_global.clear()
    return {
            "message": "All data has been deleted"
        }


# 查询指定数据
@app.get("/data/{user}",response_class=HTMLResponse)
async def get_user(
    user: str,
):
    global data_global
    if user in data_global:
        text = data_global[user].get("text", "")
        html = data_global[user].get("html", "")
        textAsHtml = data_global[user].get("textAsHtml", "")
        html_content = f"""
    <html>
        <head>
            <title>Your email</title>
        </head>
        <body>
            <p>{text}</p>
            {html}
            {textAsHtml}
        </body>
    </html>
    """
        return HTMLResponse(content=html_content, status_code=200)
    raise HTTPException(status_code=404, detail="User not found")

# 删除指定数据
@app.delete("/data/{user}")
async def delete_user(
    user: str,
):
    global data_global
    if user in data_global:

        del data_global[user]
        return {
            "message": f"{user} has been deleted"
        }
    raise HTTPException(status_code=404, detail="User not found")



#定时任务
@app.get("/api/cron")
async def cron(request: Request):
    key = request.headers.get("Authorization", "")
    if not adminkey or not key:
         raise HTTPException(status_code=400, detail="Key is incorrect")
    key  = key[7:]
    if key != adminkey:
         raise HTTPException(status_code=400, detail="Key is incorrect")
    global data_global  
    data_global.clear()
    return {
            "message": "cron",
        } 


