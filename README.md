# EmailForward 域名邮箱系统

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)

</div>

> 一个功能强大的自定义域名邮箱管理系统，支持多域名收发邮件、用户管理和API访问。

## ✨ 功能特点

- 🔄 **灵活的邮件收发**: 支持任意前缀的电子邮件接收和发送
- 👥 **多用户管理**: 完整的用户管理界面和权限控制
- 🔌 **API支持**: 提供OpenAPI接口用于程序化访问
- 🔒 **安全可靠**: 支持安全设置和CF等防护措施
- 📱 **响应式界面**: 适配各种设备的用户友好界面
- 🔄 **群发功能**: 支持批量邮件发送
- 📋 **自定义公告**: 可自定义登录页和首页公告

## 🚀 快速开始

### 部署方法

```bash
# 克隆仓库
git clone https://github.com/CatAnd-Dog/emailforward.git

# 进入项目目录
cd emailforward

# 复制配置文件
cp .env.example .env

# 编辑配置文件，设置密钥和其他选项
vim .env

# 使用Docker Compose启动服务
docker compose pull && docker compose up -d
```

### 初始登录信息

- **用户名**: `admin`
- **密码**: `admin`

> ⚠️ **安全提示**: 首次登录后请立即修改默认密码

## 📋 使用指南

### 接收邮件

如果您的域名为 `example.com`，系统将接收所有发送到 `*@example.com` 的邮件。

例如：
- `info@example.com`
- `support@example.com`
- `any-prefix@example.com`

所有这些邮件都可以在系统中查看和管理。

![接收邮件示例](https://img.opaoai.com/i/2024/12/08/67555f3aa36ec.webp)

### 发送邮件

同样，您可以使用任意前缀发送电子邮件。如果您的域名为 `example.com`，您可以配置使用：
- `support@example.com`
- `no-reply@example.com`
- 任何您需要的前缀

在发送界面，"email-from"字段表示您选择的前缀。

![发送邮件示例](https://img.opaoai.com/i/2024/12/08/67555e7746c49.webp)

## ⚙️ 配置说明

### 重要配置

1. 务必修改 `.env` 文件中的密钥设置
2. 强烈建议为服务添加CF的5秒盾或其他安全防护措施

## 🔗 资源链接

### 演示

- [在线演示 Demo](https://imail.opaoai.com)

![系统界面](https://img.opaoai.com/i/2024/12/07/67542f06b3792.webp)

### 详细教程

- [完整部署教程](https://oneperfect.cn/1335/)
- [用户管理指南](https://oneperfect.cn/1351/)
- [配置收信功能](https://oneperfect.cn/1337/)
- [配置发信功能](https://oneperfect.cn/1369/)
- [公告和自定义设置](https://oneperfect.cn/1365/)

### API文档

- [OpenAPI 使用方法](/docs/openapi.md)

## 📝 更新日志

### 2024-12-12
- ✨ 添加OpenAPI功能，支持直接通过API查询邮件
- ✨ 添加API提取验证码功能
- 🐛 修复域名空格相关bug

### 2024-12-08
- ✨ 新增登录页公告功能
- ✨ 新增首页公告功能
- ✨ 新增自定义版权信息
- ✨ 添加群发邮件功能
- 📖 [详细修改方法](https://oneperfect.cn/1365/)

## 💪 贡献

欢迎提交问题和功能请求！如果您想贡献代码，请提交Pull Request。

## 📜 许可证

本项目采用 MIT 许可证 - 详情请查看 LICENSE 文件

---

### ⭐ 如果这个项目对您有帮助，请给个 Star 支持一下！
