# 📧 EmailForward Domain Email System

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)
![Stars](https://img.shields.io/github/stars/CatAnd-Dog/emailforward?style=social)

</div>

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/07/67542f06b3792.webp" alt="EmailForward Logo" width="650">
</p>

<p align="center">
  <b>Powerful, Flexible Custom Domain Email System | Multi-Domain Support | User-Friendly Interface | API Integration</b>
</p>

<div align="center">
  <a href="https://imail.opaoai.com">🔍 Live Demo</a> •
  <a href="#-quick-start">🚀 Quick Start</a> •
  <a href="#-features">✨ Features</a> •
  <a href="#-user-guide">📋 User Guide</a> •
  <a href="#-api-documentation">🔌 API</a>
</div>

## 🌐 Languages

- [中文](../README.md)
- [English](README_EN.md) (Current)
- [日本語](README_JA.md)
- [한국어](README_KO.md)

## ✨ Features

<table>
  <tr>
    <td>
      <h3>🔄 Flexible Email Handling</h3>
      <p>Support for receiving and sending emails with any prefix, compatible with multiple domains</p>
    </td>
    <td>
      <h3>👥 Multi-User Management</h3>
      <p>Complete user management interface and refined permission control system</p>
    </td>
  </tr>
  <tr>
    <td>
      <h3>🔌 API Support</h3>
      <p>Comprehensive OpenAPI interface for programmatic access and automation</p>
    </td>
    <td>
      <h3>🔒 Secure & Reliable</h3>
      <p>Built-in security settings, compatible with Cloudflare protection</p>
    </td>
  </tr>
  <tr>
    <td>
      <h3>📱 Responsive Interface</h3>
      <p>User-friendly interface that adapts to computers, tablets, and mobile devices</p>
    </td>
    <td>
      <h3>🔄 Mass Mailing</h3>
      <p>Powerful batch email sending functionality to improve work efficiency</p>
    </td>
  </tr>
  <tr>
    <td colspan="2">
      <h3>📋 Custom Announcements</h3>
      <p>Customizable login page and homepage announcements to enhance user experience</p>
    </td>
  </tr>
</table>

## 🚀 Quick Start

### Deployment Method

```bash
# Clone repository
git clone https://github.com/CatAnd-Dog/emailforward.git

# Enter project directory
cd emailforward

# Copy configuration file
cp .env.example .env

# Edit configuration file to set keys and other options
vim .env

# Use Docker Compose to start services
docker compose pull && docker compose up -d
```

### Initial Login Information

<table>
  <tr>
    <th>Username</th>
    <th>Password</th>
  </tr>
  <tr>
    <td><code>admin</code></td>
    <td><code>admin</code></td>
  </tr>
</table>

> ⚠️ **Security Tip**: Change the default password immediately after first login

## 📋 User Guide

### 📥 Receiving Emails

If your domain is `example.com`, the system will receive all emails sent to `*@example.com`.

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/08/67555f3aa36ec.webp" alt="Receiving Email Example" width="600">
</p>

For example, you can receive emails sent to:
- `info@example.com`
- `support@example.com`
- `any-prefix@example.com`

All these emails can be viewed and managed in a unified interface.

### 📤 Sending Emails

Similarly, you can send emails using any prefix. If your domain is `example.com`, you can configure to use:

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/08/67555e7746c49.webp" alt="Sending Email Example" width="600">
</p>

- `support@example.com`
- `no-reply@example.com`
- Any prefix you need

In the sending interface, the "email-from" field represents your chosen prefix.

## ⚙️ Configuration

### Important Settings

<table>
  <tr>
    <td>🔑 <b>Key Settings</b></td>
    <td>Be sure to modify the key settings in the <code>.env</code> file</td>
  </tr>
  <tr>
    <td>🛡️ <b>Security Protection</b></td>
    <td>It is strongly recommended to add Cloudflare's 5-second protection or other security measures</td>
  </tr>
</table>

## 🔗 Resource Links

### API Documentation

- [📘 OpenAPI Usage Guide](/docs/openapi_en.md)
- [🌐 API Guide](/docs/api_guide_en.md)

## 📝 Changelog

### 2024-12-15
- 🌐 Added multi-language support (English, Japanese, Korean)
- 📚 Improved API documentation
- 🎨 Enhanced README presentation

### 2024-12-12
- ✨ Added OpenAPI functionality, supporting direct email queries via API
- ✨ Added API verification code extraction feature
- 🐛 Fixed domain space-related bugs

### 2024-12-08
- ✨ Added login page announcement feature
- ✨ Added homepage announcement feature
- ✨ Added custom copyright information
- ✨ Added mass mailing feature

## 💪 Contributing

Issues and feature requests are welcome! If you want to contribute code, please submit a Pull Request.

## 📜 License

<p>
This project is licensed under the MIT License - see the <a href="../LICENSE">LICENSE</a> file for details
</p>

---

<p align="center">
  <b>⭐ If this project helps you, please give it a star!</b>
</p>

<p align="center">
  <a href="https://github.com/CatAnd-Dog/emailforward">
    <img src="https://img.shields.io/github/stars/CatAnd-Dog/emailforward?style=social" alt="GitHub stars">
  </a>
</p>
