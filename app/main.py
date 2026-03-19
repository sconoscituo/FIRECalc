from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import calculator, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 라이프사이클 핸들러"""
    # 시작: DB 초기화
    await init_db()
    print("FIRECalc API 서버 시작됨")
    yield
    print("FIRECalc API 서버 종료됨")


app = FastAPI(
    title="FIRECalc API",
    description="FIRE 달성 계산기 + AI 로드맵 - 조기 은퇴 시뮬레이터",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 설정 (프론트엔드 연동 시 origins 수정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(users.router)
app.include_router(calculator.router)


@app.get("/", tags=["헬스체크"])
async def root():
    """API 서버 상태 확인"""
    return {
        "service": "FIRECalc",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["헬스체크"])
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy"}
