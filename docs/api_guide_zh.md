# EmailForward API 使用指南

## 简介

EmailForward 提供了 RESTful API，允许您以编程方式访问邮件数据并执行各种操作。本指南详细介绍了如何有效使用 API。

## 认证

所有 API 请求都需要使用 API 密钥进行身份验证。您可以从用户设置页面获取 API 密钥。

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://your-emailforward-instance.com/api/v1/emails
```

## API 端点

### 获取邮件列表

根据过滤条件检索邮件列表。

```
GET /api/v1/emails
```

**参数：**

- `domain`（可选）：按域名过滤
- `from`（可选）：按发件人过滤
- `to`（可选）：按收件人过滤
- `subject`（可选）：按主题过滤
- `date_from`（可选）：按日期范围起始过滤
- `date_to`（可选）：按日期范围结束过滤
- `page`（可选）：分页页码
- `limit`（可选）：每页结果数

**示例：**

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://your-emailforward-instance.com/api/v1/emails?domain=example.com&limit=10"
```

### 获取邮件详情

检索特定邮件的详细信息。

```
GET /api/v1/emails/{id}
```

**示例：**

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://your-emailforward-instance.com/api/v1/emails/123"
```

### 提取验证码

从邮件中提取验证码。

```
GET /api/v1/extract-code
```

**参数：**

- `domain`（必填）：邮箱域名
- `prefix`（必填）：邮箱前缀
- `sender`（可选）：发件人电子邮件地址
- `regex`（可选）：自定义验证码提取正则表达式

**示例：**

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://your-emailforward-instance.com/api/v1/extract-code?domain=example.com&prefix=user&sender=service@company.com"
```

## 响应格式

所有 API 响应均以 JSON 格式返回。典型的响应结构：

```json
{
  "status": "success",
  "data": [...],
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 10
  }
}
```

错误响应将包含错误消息：

```json
{
  "status": "error",
  "message": "错误描述"
}
```

## 速率限制

为防止滥用，API 请求受到速率限制。当前限制为：

- 每个 API 密钥每分钟 100 个请求
- 每个 API 密钥每天 5,000 个请求

## 示例

### Python 示例

```python
import requests

api_key = "YOUR_API_KEY"
base_url = "https://your-emailforward-instance.com/api/v1"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 获取特定域名的邮件
response = requests.get(
    f"{base_url}/emails",
    headers=headers,
    params={"domain": "example.com", "limit": 10}
)

emails = response.json()
print(f"获取到 {len(emails['data'])} 封邮件")

# 提取验证码
response = requests.get(
    f"{base_url}/extract-code",
    headers=headers,
    params={
        "domain": "example.com",
        "prefix": "user",
        "sender": "noreply@service.com"
    }
)

result = response.json()
if result["status"] == "success":
    print(f"验证码: {result['data']['code']}")
else:
    print(f"错误: {result['message']}")
```

### JavaScript 示例

```javascript
// API 配置
const apiKey = 'YOUR_API_KEY';
const baseUrl = 'https://your-emailforward-instance.com/api/v1';

// 设置请求头
const headers = {
  'Authorization': `Bearer ${apiKey}`,
  'Content-Type': 'application/json'
};

// 获取特定域名的邮件
async function getEmails() {
  try {
    const response = await fetch(`${baseUrl}/emails?domain=example.com&limit=10`, {
      method: 'GET',
      headers: headers
    });
    
    const data = await response.json();
    if (data.status === 'success') {
      console.log(`获取到 ${data.data.length} 封邮件`);
      return data.data;
    } else {
      console.error(`错误: ${data.message}`);
      return [];
    }
  } catch (error) {
    console.error('API 请求失败:', error);
    return [];
  }
}

// 提取验证码
async function extractCode() {
  const params = new URLSearchParams({
    domain: 'example.com',
    prefix: 'user',
    sender: 'noreply@service.com'
  });
  
  try {
    const response = await fetch(`${baseUrl}/extract-code?${params}`, {
      method: 'GET',
      headers: headers
    });
    
    const result = await response.json();
    if (result.status === 'success') {
      console.log(`验证码: ${result.data.code}`);
      return result.data.code;
    } else {
      console.error(`错误: ${result.message}`);
      return null;
    }
  } catch (error) {
    console.error('API 请求失败:', error);
    return null;
  }
}

// 执行函数
(async () => {
  const emails = await getEmails();
  const code = await extractCode();
})();
```

## 支持

如果您遇到任何问题或对 API 有疑问，请联系支持团队或在 GitHub 仓库中提交 Issue。
