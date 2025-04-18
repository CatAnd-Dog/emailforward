# EmailForward API Guide

## Introduction

EmailForward provides a RESTful API that allows you to programmatically access email data and perform various operations. This guide explains how to use the API effectively.

## Authentication

All API requests require authentication using an API key. You can obtain your API key from the user settings page.

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://your-emailforward-instance.com/api/v1/emails
```

## API Endpoints

### List Emails

Retrieve a list of emails based on filter criteria.

```
GET /api/v1/emails
```

**Parameters:**

- `domain` (optional): Filter by domain
- `from` (optional): Filter by sender
- `to` (optional): Filter by recipient
- `subject` (optional): Filter by subject
- `date_from` (optional): Filter by date range start
- `date_to` (optional): Filter by date range end
- `page` (optional): Page number for pagination
- `limit` (optional): Number of results per page

**Example:**

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://your-emailforward-instance.com/api/v1/emails?domain=example.com&limit=10"
```

### Get Email Details

Retrieve details of a specific email.

```
GET /api/v1/emails/{id}
```

**Example:**

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://your-emailforward-instance.com/api/v1/emails/123"
```

### Extract Verification Code

Extract verification codes from emails.

```
GET /api/v1/extract-code
```

**Parameters:**

- `domain` (required): Email domain
- `prefix` (required): Email prefix
- `sender` (optional): Sender email address
- `regex` (optional): Custom regex pattern for code extraction

**Example:**

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://your-emailforward-instance.com/api/v1/extract-code?domain=example.com&prefix=user&sender=service@company.com"
```

## Response Format

All API responses are returned in JSON format. A typical response structure:

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

Error responses will include an error message:

```json
{
  "status": "error",
  "message": "Error description"
}
```

## Rate Limiting

API requests are subject to rate limiting to prevent abuse. The current limits are:

- 100 requests per minute per API key
- 5,000 requests per day per API key

## Examples

### Python Example

```python
import requests

api_key = "YOUR_API_KEY"
base_url = "https://your-emailforward-instance.com/api/v1"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Get emails from a specific domain
response = requests.get(
    f"{base_url}/emails",
    headers=headers,
    params={"domain": "example.com", "limit": 10}
)

emails = response.json()
print(f"Retrieved {len(emails['data'])} emails")

# Extract verification code
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
    print(f"Verification code: {result['data']['code']}")
else:
    print(f"Error: {result['message']}")
```

### JavaScript Example

```javascript
// API configuration
const apiKey = 'YOUR_API_KEY';
const baseUrl = 'https://your-emailforward-instance.com/api/v1';

// Set up headers
const headers = {
  'Authorization': `Bearer ${apiKey}`,
  'Content-Type': 'application/json'
};

// Get emails from a specific domain
async function getEmails() {
  try {
    const response = await fetch(`${baseUrl}/emails?domain=example.com&limit=10`, {
      method: 'GET',
      headers: headers
    });
    
    const data = await response.json();
    if (data.status === 'success') {
      console.log(`Retrieved ${data.data.length} emails`);
      return data.data;
    } else {
      console.error(`Error: ${data.message}`);
      return [];
    }
  } catch (error) {
    console.error('API request failed:', error);
    return [];
  }
}

// Extract verification code
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
      console.log(`Verification code: ${result.data.code}`);
      return result.data.code;
    } else {
      console.error(`Error: ${result.message}`);
      return null;
    }
  } catch (error) {
    console.error('API request failed:', error);
    return null;
  }
}

// Execute functions
(async () => {
  const emails = await getEmails();
  const code = await extractCode();
})();
```

## Support

If you encounter any issues or have questions about the API, please contact support or open an issue in the GitHub repository.
