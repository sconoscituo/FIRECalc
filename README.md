# FIRECalc

FIRE(Financial Independence, Retire Early) 달성 계산기 + AI 로드맵 서비스

## 기능

### 무료 플랜
- FIRE 달성 기간 계산 (복리, 인플레이션, 4% 룰 적용)
- 월 저축액 목표 계산
- Trinity Study 기반 안전 인출율 분석

### 프리미엄 플랜
- 다양한 시나리오 비교 분석 (공격적/보수적/균형)
- Gemini AI 맞춤 FIRE 달성 로드맵
- 월간 재무 리포트
- 지출 최적화 전략 제안

## 기술 스택

- **백엔드**: FastAPI + SQLAlchemy (aiosqlite)
- **AI**: Google Gemini AI
- **계산 엔진**: 복리/인플레이션/4% 룰 직접 구현
- **인증**: JWT (python-jose)

## 시작하기

```bash
# 1. 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 API 키 입력

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 서버 실행
uvicorn app.main:app --reload
```

## Docker로 실행

```bash
docker-compose up -d
```

## API 문서

서버 실행 후 http://localhost:8000/docs 에서 Swagger UI 확인

## FIRE 계산 방식

- **4% 룰**: 연간 지출의 25배 = FIRE 목표 자산
- **Trinity Study**: 역사적 데이터 기반 안전 인출율
- **복리 계산**: 월 복리 적용
- **인플레이션**: 실질 수익률 반영

## 환경변수

| 변수명 | 설명 |
|--------|------|
| `GEMINI_API_KEY` | Google Gemini AI API 키 |
| `DATABASE_URL` | 데이터베이스 URL |
| `SECRET_KEY` | JWT 서명용 시크릿 키 |

## 수익 구조

- 무료: 기본 FIRE 계산
- 프리미엄: 월 $7.99 - 시나리오 비교 + AI 로드맵 + 월간 리포트
