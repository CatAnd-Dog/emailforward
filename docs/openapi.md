# openapi的使用说明

### 请求地址
yourdoami/openapi  
http://127.0.0.1:8000/openapi
### 通过请求头传递key
两种传递方式，均可  
X-API-Key :   key   
Authorization: Bearer key

### 提取指定邮件数 
/record/emails  
post 数据   
例   
```
{
    "username": "user",
    "email_user": "ssssss", 
    "email_domain": "ami.458741.xyz",
    "num": 10   可选
}
```

说明：   
username 为用户名   
email_user  为收件邮箱前缀   
email_domain 为收件邮箱域名，不要 @   
num  提取邮件数量

### 提取验证码

/record/code/{username}  
或者 不使用请求头，直接传参 key
/record/code/{username}?key=你的key
get 数据  
正则规则
```
pattern = re.compile(
        r"(?i)(?:验证码|驗證碼|captcha|code|verify|check|auth|token|pw|pass|password|verification)\s*[:：]?\s*([A-Za-z0-9]{4,20})"
    )
```
