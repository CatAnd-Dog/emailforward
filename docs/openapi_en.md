# EmailForward OpenAPI Documentation

<div align="center">
  
![API Version](https://img.shields.io/badge/API%20Version-v1-blue)
![Status](https://img.shields.io/badge/Status-Stable-green)
  
</div>

## 📋 Contents

- [Introduction](#introduction)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Get Email List](#get-email-list)
  - [Extract Verification Code](#extract-verification-code)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Code Examples](#code-examples)
- [Rate Limiting](#rate-limiting)

## Introduction

EmailForward provides a RESTful API that allows you to programmatically access email data and perform various operations. This document details the API usage and features.

## Authentication

All API requests require authentication using an API key. You can obtain your API key from the user settings page.

Two methods of authentication are supported:

```
X-API-Key: YOUR_API_KEY
```

or

```
Authorization: Bearer YOUR_API_KEY
```

## API Endpoints

### Get Email List

**Endpoint:** `/record/emails`  
**Method:** POST  
**Description:** Retrieve a list of emails based on specified criteria

**Request Parameters:**

```json
{
    "username": "user",           // Required, username
    "email_user": "support",      // Required, email prefix
    "email_domain": "example.com", // Required, email domain (without @ symbol)
    "num": 10,                    // Optional, number of emails to retrieve, default is 10
    "date_from": "2024-01-01",    // Optional, start date filter
    "date_to": "2024-12-31",      // Optional, end date filter
    "sender": "noreply@service.com" // Optional, sender filter
}
```

**Response Example:**

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
        // ...more emails
    ],
    "meta": {
        "total": 45,
        "retrieved": 10
    }
}
```

### Extract Verification Code

**Endpoint:** `/record/code/{username}`  
**Method:** GET  
**Description:** Extract verification codes from emails

**URL Parameters:**
- `username`: The username

**Query Parameters:**
- `key` (optional): API key if not passed via headers
- `domain` (required): Email domain
- `prefix` (required): Email prefix
- `sender` (optional): Filter by sender
- `regex` (optional): Custom regular expression for code extraction

**Default Regular Expression:**
```
r"(?i)(?:验证码|驗證碼|captcha|code|verify|check|auth|token|pw|pass|password|verification)\s*[:：]?\s*([A-Za-z0-9]{4,20})"
```

This regex matches common verification code patterns such as:
- Verification Code: 123456
- Your auth code is: XYZ789
- Code: ABC123

**Response Example:**

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

## Response Format

All API responses are returned in JSON format with the following general structure:

**Success Response:**
```json
{
    "status": "success",
    "data": {...},
    "meta": {...}  // Optional, contains pagination or other metadata
}
```

**Error Response:**
```json
{
    "status": "error",
    "message": "Error description",
    "code": 404  // HTTP status code
}
```

## Error Handling

Common error status codes:

| Status Code | Description |
|-------------|-------------|
| 400         | Bad request or missing parameters |
| 401         | Authentication failed |
| 403         | Insufficient permissions |
| 404         | Resource not found |
| 429         | Rate limit exceeded |
| 500         | Internal server error |

## Code Examples

### Python Example

```python
import requests
import json

# Configuration
api_key = "YOUR_API_KEY"
base_url = "https://your-emailforward-instance.com"

# Set request headers
headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

# Get email list
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

# Extract verification code
def extract_code():
    url = f"{base_url}/record/code/user"
    params = {
        "domain": "example.com",
        "prefix": "support",
        "sender": "noreply@service.com"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Execute
emails = get_emails()
print(f"Retrieved {len(emails['data'])} emails")

code_info = extract_code()
if code_info['status'] == 'success':
    print(f"Verification code: {code_info['data']['code']}")
else:
    print(f"Error: {code_info['message']}")
```

### JavaScript Example

```javascript
// API configuration
const apiKey = "YOUR_API_KEY";
const baseUrl = "https://your-emailforward-instance.com";

// Get email list
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

// Extract verification code
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

// Usage example
(async () => {
    try {
        const emails = await getEmails();
        console.log(`Retrieved ${emails.data.length} emails`);
        
        const codeInfo = await extractCode();
        if (codeInfo.status === 'success') {
            console.log(`Verification code: ${codeInfo.data.code}`);
        } else {
            console.log(`Error: ${codeInfo.message}`);
        }
    } catch (error) {
        console.error("Request error:", error);
    }
})();
```

## Rate Limiting

To prevent abuse, API requests are subject to rate limiting:

- **100** requests per minute per API key
- **5,000** requests per day per API key

When the limit is exceeded, the API will return a `429 Too Many Requests` status code.

---

If you have any questions or suggestions, please contact the system administrator or submit a GitHub issue.
