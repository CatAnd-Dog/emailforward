# openapi的使用说明

### 请求地址
yourdoami/openapi/record/emails
http://127.0.0.1:8000/openapi/record/emails
### 通过请求头传递key
两种传递方式，均可  
X-API-Key :   key   
Authorization: Bearer key

post 数据   
例   
```
{
    "username": "user",
    "email_user": "ssssss", 可选
    "email_domain": "ami.458741.xyz",
    "num": 10   可选
}
```

说明：   
username 为用户名   
email_user  为收件邮箱前缀   
email_domain 为收件邮箱域名，不要 @   
num  提取邮件数量
