# FIRECalc - 설정 및 사용 가이드

## 프로젝트 소개

FIRE(Financial Independence, Retire Early) 달성 시뮬레이터로, 재무 프로필을 입력하면 조기 은퇴 가능 시점을 계산하고 Gemini AI가 개인 맞춤형 투자 로드맵을 생성하는 서비스입니다.

---

## 필요한 API 키 / 환경변수 목록

| 변수명 | 설명 | 발급 URL |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini AI API 키 | https://aistudio.google.com/app/apikey |
| `SECRET_KEY` | JWT 서명용 비밀 키 | 직접 생성 (예: `openssl rand -hex 32`) |
| `DATABASE_URL` | 데이터베이스 연결 URL (기본: SQLite) | - |
| `DEFAULT_INFLATION_RATE` | 기본 인플레이션율 (기본: 0.03 = 3%) | - |
| `DEFAULT_EXPECTED_RETURN` | 기본 기대 수익률 (기본: 0.07 = 7%) | - |
| `SAFE_WITHDRAWAL_RATE` | 안전 인출율 - 4% 룰 (기본: 0.04) | - |

---

## GitHub Secrets 설정 방법

저장소 페이지 > **Settings** > **Secrets and variables** > **Actions** > **New repository secret**

| Secret 이름 | 값 |
|---|---|
| `GEMINI_API_KEY` | Google AI Studio에서 발급한 키 |
| `SECRET_KEY` | 프로덕션용 JWT 비밀 키 |

---

## 로컬 개발 환경 설정

### 1. `.env` 파일 생성

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite+aiosqlite:///./firecalc.db
DEFAULT_INFLATION_RATE=0.03
DEFAULT_EXPECTED_RETURN=0.07
SAFE_WITHDRAWAL_RATE=0.04
DEBUG=false
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

---

## 실행 방법

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버 실행 후 http://localhost:8000/docs 에서 Swagger UI를 확인할 수 있습니다.

### Docker로 실행

```bash
docker-compose up --build
```

---

## API 엔드포인트 주요 사용법

### 헬스 체크

```
GET /health
```

### 회원가입

```
POST /users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

### 로그인 (JWT 토큰 발급)

```
POST /users/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

응답으로 받은 `access_token`을 이후 요청의 `Authorization: Bearer <token>` 헤더에 포함합니다.

### 재무 프로필 저장 (생성 또는 수정)

```
POST /calculator/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_age": 30,
  "monthly_income": 5000000,
  "monthly_expense": 3000000,
  "current_assets": 50000000,
  "monthly_savings": 1500000,
  "expected_return": 0.07,
  "inflation_rate": 0.03,
  "target_retirement_age": 45
}
```

### FIRE 달성 시뮬레이션 실행

```
GET /calculator/fire
Authorization: Bearer <access_token>
```

응답에 `fire_number`(필요 자산), `years_to_fire`(달성까지 년수), `retirement_date`(예상 은퇴일), `monthly_projection`(월별 자산 추이) 포함.

### 시나리오 비교 (여러 조건 비교)

```
POST /calculator/scenarios/compare
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "scenarios": [
    {"label": "현재 저축률", "monthly_savings": 1500000},
    {"label": "저축률 20% 증가", "monthly_savings": 1800000},
    {"label": "투자 수익률 8%", "monthly_savings": 1500000, "expected_return": 0.08}
  ]
}
```

### AI 투자 로드맵 생성 (프리미엄)

```
POST /calculator/roadmap
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "focus": "투자 포트폴리오 최적화"
}
```

---

전체 API 문서: http://localhost:8000/docs
