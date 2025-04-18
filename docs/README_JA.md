# 📧 EmailForward ドメインメールシステム

<div align="center">

![バージョン](https://img.shields.io/badge/バージョン-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)
![Stars](https://img.shields.io/github/stars/CatAnd-Dog/emailforward?style=social)

</div>

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/07/67542f06b3792.webp" alt="EmailForward Logo" width="650">
</p>

<p align="center">
  <b>強力で柔軟なカスタムドメインメールシステム | マルチドメイン対応 | ユーザーフレンドリーな界面 | API連携</b>
</p>

<div align="center">
  <a href="https://imail.opaoai.com">🔍 ライブデモ</a> •
  <a href="#-クイックスタート">🚀 クイックスタート</a> •
  <a href="#-特徴">✨ 特徴</a> •
  <a href="#-ユーザーガイド">📋 ユーザーガイド</a> •
  <a href="#-apiドキュメント">🔌 API</a>
</div>

## 🌐 言語

- [中文](../README.md)
- [English](README_EN.md)
- [日本語](README_JA.md) (現在)
- [한국어](README_KO.md)

## ✨ 特徴

<table>
  <tr>
    <td>
      <h3>🔄 柔軟なメール処理</h3>
      <p>あらゆるプレフィックスでのメールの受信と送信をサポート、複数ドメインに対応</p>
    </td>
    <td>
      <h3>👥 マルチユーザー管理</h3>
      <p>完全なユーザー管理インターフェースと精密な権限制御システム</p>
    </td>
  </tr>
  <tr>
    <td>
      <h3>🔌 API対応</h3>
      <p>プログラムによるアクセスと自動化のための総合的なOpenAPIインターフェース</p>
    </td>
    <td>
      <h3>🔒 安全で信頼性の高い</h3>
      <p>内蔵セキュリティ設定、Cloudflare保護と互換性あり</p>
    </td>
  </tr>
  <tr>
    <td>
      <h3>📱 レスポンシブインターフェース</h3>
      <p>PC、タブレット、モバイルデバイスに適応するユーザーフレンドリーなインターフェース</p>
    </td>
    <td>
      <h3>🔄 一括メール送信</h3>
      <p>作業効率を向上させる強力な一括メール送信機能</p>
    </td>
  </tr>
  <tr>
    <td colspan="2">
      <h3>📋 カスタム通知</h3>
      <p>ユーザーエクスペリエンスを向上させるためにカスタマイズ可能なログインページとホームページのお知らせ</p>
    </td>
  </tr>
</table>

## 🚀 クイックスタート

### デプロイメント方法

```bash
# リポジトリをクローン
git clone https://github.com/CatAnd-Dog/emailforward.git

# プロジェクトディレクトリに移動
cd emailforward

# 設定ファイルをコピー
cp .env.example .env

# 設定ファイルを編集して、キーやその他のオプションを設定
vim .env

# Docker Composeを使用してサービスを起動
docker compose pull && docker compose up -d
```

### 初期ログイン情報

<table>
  <tr>
    <th>ユーザー名</th>
    <th>パスワード</th>
  </tr>
  <tr>
    <td><code>admin</code></td>
    <td><code>admin</code></td>
  </tr>
</table>

> ⚠️ **セキュリティヒント**: 初回ログイン後すぐにデフォルトパスワードを変更してください

## 📋 ユーザーガイド

### 📥 メールの受信

ドメインが `example.com` の場合、システムは `*@example.com` に送信されたすべてのメールを受信します。

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/08/67555f3aa36ec.webp" alt="メール受信の例" width="600">
</p>

例えば、次の宛先に送信されたメールを受信できます：
- `info@example.com`
- `support@example.com`
- `any-prefix@example.com`

これらのすべてのメールは統一されたインターフェースで表示および管理できます。

### 📤 メールの送信

同様に、任意のプレフィックスを使用してメールを送信できます。ドメインが `example.com` の場合、以下を設定できます：

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/08/67555e7746c49.webp" alt="メール送信の例" width="600">
</p>

- `support@example.com`
- `no-reply@example.com`
- 必要な任意のプレフィックス

送信インターフェースでは、「email-from」フィールドが選択したプレフィックスを表します。

## ⚙️ 設定

### 重要な設定

<table>
  <tr>
    <td>🔑 <b>キー設定</b></td>
    <td><code>.env</code>ファイル内のキー設定を必ず変更してください</td>
  </tr>
  <tr>
    <td>🛡️ <b>セキュリティ保護</b></td>
    <td>Cloudflareの5秒間の保護や他のセキュリティ対策を追加することを強くお勧めします</td>
  </tr>
</table>

## 🔗 リソースリンク

### APIドキュメント

- [📘 OpenAPI使用ガイド](/docs/openapi_ja.md)
- [🌐 APIガイド](/docs/api_guide_en.md)

## 📝 変更履歴

### 2024-12-15
- 🌐 多言語サポートを追加（英語、日本語、韓国語）
- 📚 APIドキュメントを改善
- 🎨 README表示を強化

### 2024-12-12
- ✨ OpenAPI機能を追加し、API経由で直接メールクエリをサポート
- ✨ API認証コード抽出機能を追加
- 🐛 ドメインスペース関連のバグを修正

### 2024-12-08
- ✨ ログインページのお知らせ機能を追加
- ✨ ホームページのお知らせ機能を追加
- ✨ カスタム著作権情報を追加
- ✨ 一括メール送信機能を追加

## 💪 貢献

問題や機能リクエストは大歓迎です！コードに貢献したい場合は、Pull Requestを提出してください。

## 📜 ライセンス

<p>
このプロジェクトはMITライセンスの下でライセンスされています - 詳細は<a href="../LICENSE">LICENSE</a>ファイルをご覧ください
</p>

---

<p align="center">
  <b>⭐ このプロジェクトが役立った場合は、スターを付けてサポートしてください！</b>
</p>

<p align="center">
  <a href="https://github.com/CatAnd-Dog/emailforward">
    <img src="https://img.shields.io/github/stars/CatAnd-Dog/emailforward?style=social" alt="GitHub stars">
  </a>
</p>
