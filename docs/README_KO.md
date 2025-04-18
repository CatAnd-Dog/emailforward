# 📧 EmailForward 도메인 이메일 시스템

<div align="center">

![버전](https://img.shields.io/badge/버전-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)
![Stars](https://img.shields.io/github/stars/CatAnd-Dog/emailforward?style=social)

</div>

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/07/67542f06b3792.webp" alt="EmailForward Logo" width="650">
</p>

<p align="center">
  <b>강력하고 유연한 맞춤형 도메인 이메일 시스템 | 다중 도메인 지원 | 사용자 친화적 인터페이스 | API 통합</b>
</p>

<div align="center">
  <a href="https://imail.opaoai.com">🔍 라이브 데모</a> •
  <a href="#-빠른-시작">🚀 빠른 시작</a> •
  <a href="#-기능">✨ 기능</a> •
  <a href="#-사용자-가이드">📋 사용자 가이드</a> •
  <a href="#-api-문서">🔌 API</a>
</div>

## 🌐 언어

- [中文](../README.md)
- [English](README_EN.md)
- [日本語](README_JA.md)
- [한국어](README_KO.md) (현재)

## ✨ 기능

<table>
  <tr>
    <td>
      <h3>🔄 유연한 이메일 처리</h3>
      <p>모든 접두사로 이메일 수신 및 발신 지원, 다중 도메인 호환</p>
    </td>
    <td>
      <h3>👥 다중 사용자 관리</h3>
      <p>완전한 사용자 관리 인터페이스 및 정교한 권한 제어 시스템</p>
    </td>
  </tr>
  <tr>
    <td>
      <h3>🔌 API 지원</h3>
      <p>프로그래밍 방식 접근 및 자동화를 위한 포괄적인 OpenAPI 인터페이스</p>
    </td>
    <td>
      <h3>🔒 안전하고 신뢰할 수 있는</h3>
      <p>내장 보안 설정, Cloudflare 보호와 호환</p>
    </td>
  </tr>
  <tr>
    <td>
      <h3>📱 반응형 인터페이스</h3>
      <p>컴퓨터, 태블릿 및 모바일 장치에 적응하는 사용자 친화적 인터페이스</p>
    </td>
    <td>
      <h3>🔄 대량 메일링</h3>
      <p>작업 효율성을 향상시키는 강력한 일괄 이메일 발송 기능</p>
    </td>
  </tr>
  <tr>
    <td colspan="2">
      <h3>📋 맞춤 공지사항</h3>
      <p>사용자 경험을 향상시키기 위해 로그인 페이지 및 홈페이지 공지사항 맞춤 설정 가능</p>
    </td>
  </tr>
</table>

## 🚀 빠른 시작

### 배포 방법

```bash
# 저장소 복제
git clone https://github.com/CatAnd-Dog/emailforward.git

# 프로젝트 디렉토리 진입
cd emailforward

# 설정 파일 복사
cp .env.example .env

# 키 및 기타 옵션을 설정하기 위해 설정 파일 편집
vim .env

# Docker Compose를 사용하여 서비스 시작
docker compose pull && docker compose up -d
```

### 초기 로그인 정보

<table>
  <tr>
    <th>사용자 이름</th>
    <th>비밀번호</th>
  </tr>
  <tr>
    <td><code>admin</code></td>
    <td><code>admin</code></td>
  </tr>
</table>

> ⚠️ **보안 팁**: 첫 로그인 후 즉시 기본 비밀번호를 변경하세요

## 📋 사용자 가이드

### 📥 이메일 수신

도메인이 `example.com`인 경우, 시스템은 `*@example.com`으로 전송된 모든 이메일을 수신합니다.

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/08/67555f3aa36ec.webp" alt="이메일 수신 예시" width="600">
</p>

예를 들어, 다음 주소로 전송된 이메일을 수신할 수 있습니다:
- `info@example.com`
- `support@example.com`
- `any-prefix@example.com`

이 모든 이메일은 통합 인터페이스에서 보고 관리할 수 있습니다.

### 📤 이메일 발송

마찬가지로, 모든 접두사를 사용하여 이메일을 보낼 수 있습니다. 도메인이 `example.com`인 경우, 다음을 구성할 수 있습니다:

<p align="center">
  <img src="https://img.opaoai.com/i/2024/12/08/67555e7746c49.webp" alt="이메일 발송 예시" width="600">
</p>

- `support@example.com`
- `no-reply@example.com`
- 필요한 모든 접두사

발송 인터페이스에서 "email-from" 필드는 선택한 접두사를 나타냅니다.

## ⚙️ 설정

### 중요 설정

<table>
  <tr>
    <td>🔑 <b>키 설정</b></td>
    <td><code>.env</code> 파일의 키 설정을 반드시 수정하세요</td>
  </tr>
  <tr>
    <td>🛡️ <b>보안 보호</b></td>
    <td>Cloudflare의 5초 보호 또는 다른 보안 조치를 추가하는 것을 강력히 권장합니다</td>
  </tr>
</table>

## 🔗 리소스 링크

### API 문서

- [📘 OpenAPI 사용 가이드](/docs/openapi_ko.md)
- [🌐 API 가이드](/docs/api_guide_en.md)

## 📝 변경 로그

### 2024-12-15
- 🌐 다국어 지원 추가 (영어, 일본어, 한국어)
- 📚 API 문서 개선
- 🎨 README 표시 향상

### 2024-12-12
- ✨ OpenAPI 기능 추가, API를 통한 직접 이메일 쿼리 지원
- ✨ API 인증 코드 추출 기능 추가
- 🐛 도메인 공백 관련 버그 수정

### 2024-12-08
- ✨ 로그인 페이지 공지 기능 추가
- ✨ 홈페이지 공지 기능 추가
- ✨ 맞춤 저작권 정보 추가
- ✨ 대량 메일링 기능 추가

## 💪 기여

이슈와 기능 요청은 언제나 환영합니다! 코드에 기여하고 싶다면 Pull Request를 제출해 주세요.

## 📜 라이선스

<p>
이 프로젝트는 MIT 라이선스 하에 라이선스가 부여됩니다 - 자세한 내용은 <a href="../LICENSE">LICENSE</a> 파일을 참조하세요
</p>

---

<p align="center">
  <b>⭐ 이 프로젝트가 도움이 된다면, 스타를 눌러 지원해 주세요!</b>
</p>

<p align="center">
  <a href="https://github.com/CatAnd-Dog/emailforward">
    <img src="https://img.shields.io/github/stars/CatAnd-Dog/emailforward?style=social" alt="GitHub stars">
  </a>
</p>
