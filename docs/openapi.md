# EmailForward OpenAPI 使用说明

<div align="center">
  
![API版本](https://img.shields.io/badge/API版本-v1-blue)
![状态](https://img.shields.io/badge/状态-稳定-green)
  
</div>

## 📋 目录

- [简介](#简介)
- [认证方式](#认证方式)
- [API端点](#api端点)
  - [获取邮件列表](#获取邮件列表)
  - [提取验证码](#提取验证码)
- [响应格式](#响应格式)
- [错误处理](#错误处理)
- [示例代码](#示例代码)
- [限流规则](#限流规则)

## 简介

EmailForward提供了RESTful API，允许您以编程方式访问邮件数据并执行各种操作。此文档详细介绍了API的使用方法和功能。

## 认证方式

所有API请求都需要使用API密钥进行身份验证。您可以从用户设置页面获取API密钥。

支持两种传递方式：

```
X-API-Key: YOUR_API_KEY
```

或者

```
Authorization: Bearer YOUR_API_KEY
```

## API端点

### 获取邮件列表

**请求地址:** `/record/emails`  
**方法:** POST  
**描述:** 获取指定条件下的邮件列表

**请求参数:**

```json
{
    "username": "user",           // 必填，用户名
    "email_user": "support",      // 必填，收件邮箱前缀
    "email_domain": "example.com", // 必填，收件邮箱域名（无需@符号）
    "num": 10,                    // 可选，获取邮件数量，默认为最新10封
    "date_from": "2024-01-01",    // 可选，起始日期过滤
    "date_to": "2024-12-31",      // 可选，结束日期过滤
    "sender": "noreply@service.com" // 可选，发件人过滤
}
```

**响应示例:**

```json
{
    "status": "success",
    "data": [
        {
            "id": "12345",
            "date": "2024-05-15T08:30:45",
            "sender": "noreply@service.com",
            "recipient": "support@example.com",
            "subject": "Your Account Verification",
            "content": "Your verification code is: 123456",
            "attachments": []
        },
        // ...更多邮件
    ],
    "meta": {
        "total": 45,
        "retrieved": 10
    }
}
```

### 提取验证码

**请求地址:** `/record/code/{username}`  
**方法:** GET  
**描述:** 从邮件中提取验证码

**URL参数:**
- `username`: 用户名

**查询参数:**
- `key` (可选): API密钥，如未通过请求头传递
- `domain` (必填): 邮箱域名
- `prefix` (必填): 邮箱前缀
- `sender` (可选): 发件人筛选
- `regex` (可选): 自定义验证码提取正则表达式

**默认正则表达式:**
```
r"(?i)(?:验证码|驗證碼|captcha|code|verify|check|auth|token|pw|pass|password|verification)\s*[:：]?\s*([A-Za-z0-9]{4,20})"
```

该正则表达式会匹配常见的验证码模式，如：
- 验证码: 123456
- 验证码：123456
- Verification Code: ABC123
- Your auth code is: XYZ789

**响应示例:**

```json
{
    "status": "success",
    "data": {
        "code": "123456",
        "email_id": "12345",
        "date": "2024-05-15T08:30:45",
        "sender": "noreply@service.com",
        "subject": "Your Account Verification"
    }
}
```

## 响应格式

所有API响应均以JSON格式返回，包含以下通用结构：

**成功响应:**
```json
{
    "status": "success",
    "data": {...},
    "meta": {...}  // 可选，包含分页或其他元数据
}
```

**错误响应:**
```json
{
    "status": "error",
    "message": "错误描述",
    "code": 404  // HTTP状态码
}
```

## 错误处理

常见错误状态码：

| 状态码 | 描述 |
|--------|------|
| 400    | 请求参数错误或缺失 |
| 401    | 认证失败 |
| 403    | 权限不足 |
| 404    | 资源未找到 |
| 429    | 请求频率超限 |
| 500    | 服务器内部错误 |

## 示例代码

### Python示例

```python
import requests
import json

# 配置
api_key = "YOUR_API_KEY"
base_url = "https://your-emailforward-instance.com"

# 设置请求头
headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

# 获取邮件列表
def get_emails():
    url = f"{base_url}/record/emails"
    payload = {
        "username": "user",
        "email_user": "support",
        "email_domain": "example.com",
        "num": 5
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 提取验证码
def extract_code():
    url = f"{base_url}/record/code/user"
    params = {
        "domain": "example.com",
        "prefix": "support",
        "sender": "noreply@service.com"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 执行
emails = get_emails()
print(f"获取到 {len(emails['data'])} 封邮件")

code_info = extract_code()
if code_info['status'] == 'success':
    print(f"验证码: {code_info['data']['code']}")
else:
    print(f"错误: {code_info['message']}")
```

### JavaScript示例

```javascript
// API配置
const apiKey = "YOUR_API_KEY";
const baseUrl = "https://your-emailforward-instance.com";

// 获取邮件列表
async function getEmails() {
    const response = await fetch(`${baseUrl}/record/emails`, {
        method: 'POST',
        headers: {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: "user",
            email_user: "support",
            email_domain: "example.com",
            num: 5
        })
    });
    return await response.json();
}

// 提取验证码
async function extractCode() {
    const params = new URLSearchParams({
        domain: "example.com",
        prefix: "support",
        sender: "noreply@service.com"
    });
    const response = await fetch(`${baseUrl}/record/code/user?${params}`, {
        headers: {
            'X-API-Key': apiKey
        }
    });
    return await response.json();
}

// 使用示例
(async () => {
    try {
        const emails = await getEmails();
        console.log(`获取到 ${emails.data.length} 封邮件`);
        
        const codeInfo = await extractCode();
        if (codeInfo.status === 'success') {
            console.log(`验证码: ${codeInfo.data.code}`);
        } else {
            console.log(`错误: ${codeInfo.message}`);
        }
    } catch (error) {
        console.error("请求出错:", error);
    }
})();
```

## 限流规则

为防止滥用，API请求受到限流保护：

- 每个API密钥每分钟可发送 **100** 个请求
- 每个API密钥每天可发送 **5,000** 个请求

超出限制时，API将返回 `429 Too Many Requests` 状态码。

---

如有任何问题或建议，请联系系统管理员或提交GitHub issue。
