# 📧 EmailForward 域名邮箱系统

<div align="center">

![版本](https://img.shields.io/badge/版本-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)
![Stars](https://img.shields.io/github/stars/CatAnd-Dog/emailforward?style=social)

</div>

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/07/67542f06b3792.webp" alt="EmailForward Logo" width="650">
</p>

<p align="center">
  <b>强大、灵活的自定义域名邮箱系统 | 多域名支持 | 用户友好界面 | API 集成</b>
</p>

<div align="center">
  <a href="https://imail.opaoai.com">🔍 在线演示</a> •
  <a href="#-快速开始">🚀 快速开始</a> •
  <a href="#-功能特点">✨ 功能特点</a> •
  <a href="#-使用指南">📋 使用指南</a> •
  <a href="#-api-文档">🔌 API</a>
</div>

## 🌐 语言 / Languages

- [中文](README.md) (当前)
- [English](docs/README_EN.md)
- [日本語](docs/README_JA.md)
- [한국어](docs/README_KO.md)

## ✨ 功能特点

<table>
  <tr>
    <td>
      <h3>🔄 灵活的邮件收发</h3>
      <p>支持任意前缀的电子邮件接收和发送，兼容多域名</p>
    </td>
    <td>
      <h3>👥 多用户管理</h3>
      <p>完整的用户管理界面和精细的权限控制体系</p>
    </td>
  </tr>
  <tr>
    <td>
      <h3>🔌 API支持</h3>
      <p>全面的OpenAPI接口，支持程序化访问和自动化操作</p>
    </td>
    <td>
      <h3>🔒 安全可靠</h3>
      <p>内置安全设置，兼容Cloudflare等防护措施</p>
    </td>
  </tr>
  <tr>
    <td>
      <h3>📱 响应式界面</h3>
      <p>适配电脑、平板和手机等各类设备的用户友好界面</p>
    </td>
    <td>
      <h3>🔄 群发功能</h3>
      <p>强大的批量邮件发送功能，提升工作效率</p>
    </td>
  </tr>
  <tr>
    <td colspan="2">
      <h3>📋 自定义公告</h3>
      <p>可根据需要自定义登录页和首页公告，增强用户体验</p>
    </td>
  </tr>
</table>

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

<table>
  <tr>
    <th>用户名</th>
    <th>密码</th>
  </tr>
  <tr>
    <td><code>admin</code></td>
    <td><code>admin</code></td>
  </tr>
</table>

> ⚠️ **安全提示**: 首次登录后请立即修改默认密码

## 📋 使用指南

### 📥 接收邮件

如果您的域名为 `example.com`，系统将接收所有发送到 `*@example.com` 的邮件。

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/08/67555f3aa36ec.webp" alt="接收邮件示例" width="600">
</p>

例如，您可以接收发送到以下地址的邮件：
- `info@example.com`
- `support@example.com`
- `any-prefix@example.com`

所有这些邮件都可以在统一的界面中查看和管理。

### 📤 发送邮件

同样，您可以使用任意前缀发送电子邮件。如果您的域名为 `example.com`，您可以配置使用：

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/08/67555e7746c49.webp" alt="发送邮件示例" width="600">
</p>

- `support@example.com`
- `no-reply@example.com`
- 任何您需要的前缀

在发送界面，"email-from"字段表示您选择的前缀。

## ⚙️ 配置说明

### 重要配置

<table>
  <tr>
    <td>🔑 <b>密钥设置</b></td>
    <td>务必修改 <code>.env</code> 文件中的密钥设置</td>
  </tr>
  <tr>
    <td>🛡️ <b>安全防护</b></td>
    <td>强烈建议为服务添加CF的5秒盾或其他安全防护措施</td>
  </tr>
</table>

## 🔗 资源链接

### 教程指南

<table>
  <tr>
    <td><a href="https://oneperfect.cn/1335/">📚 完整部署教程</a></td>
    <td><a href="https://oneperfect.cn/1351/">👥 用户管理指南</a></td>
  </tr>
  <tr>
    <td><a href="https://oneperfect.cn/1337/">📥 配置收信功能</a></td>
    <td><a href="https://oneperfect.cn/1369/">📤 配置发信功能</a></td>
  </tr>
  <tr>
    <td colspan="2"><a href="https://oneperfect.cn/1365/">📋 公告和自定义设置</a></td>
  </tr>
</table>

### API 文档

- [📘 OpenAPI 使用方法](/docs/openapi.md)
- [🌐 API 使用指南 (English)](/docs/api_guide_en.md)

## 📝 更新日志

### 2024-12-15
- 🌐 添加多语言支持（英语、日语、韩语）
- 📚 完善API文档
- 🎨 美化项目README展示

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

<p>
本项目采用 MIT 许可证 - 详情请查看 <a href="LICENSE">LICENSE</a> 文件
</p>

---

<p align="center">
  <b>⭐ 如果这个项目对您有帮助，请给个 Star 支持一下！</b>
</p>

<p align="center">
  <a href="https://github.com/CatAnd-Dog/emailforward">
    <img src="https://img.shields.io/github/stars/CatAnd-Dog/emailforward?style=social" alt="GitHub stars">
  </a>
</p>
