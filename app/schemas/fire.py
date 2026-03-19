from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── 사용자 스키마 ──────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_premium: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── 재무 프로필 스키마 ──────────────────────────────────────────

class ProfileCreate(BaseModel):
    """재무 프로필 생성/수정 요청"""
    age: int = Field(..., ge=18, le=80, description="현재 나이")
    current_assets: float = Field(..., ge=0, description="현재 총 자산 (만원)")
    monthly_income: float = Field(..., gt=0, description="월 수입 (만원)")
    monthly_expense: float = Field(..., gt=0, description="월 지출 (만원)")
    target_amount: Optional[float] = Field(None, description="FIRE 목표 자산 (미입력 시 4% 룰로 자동 계산)")
    expected_return_rate: float = Field(0.07, ge=0.01, le=0.30, description="연 기대 수익률")
    inflation_rate: float = Field(0.03, ge=0.0, le=0.20, description="연 인플레이션율")


class ProfileResponse(BaseModel):
    """재무 프로필 응답"""
    id: int
    age: int
    current_assets: float
    monthly_income: float
    monthly_expense: float
    monthly_savings: float          # 월 저축액 (income - expense)
    target_amount: Optional[float]
    expected_return_rate: float
    inflation_rate: float
    created_at: datetime

    model_config = {"from_attributes": True}


# ── FIRE 계산 결과 스키마 ──────────────────────────────────────

class FireResult(BaseModel):
    """FIRE 계산 결과"""
    # 입력 요약
    current_assets: float
    monthly_savings: float
    annual_savings: float

    # FIRE 목표
    fire_amount: float             # FIRE 목표 자산 (만원)
    fire_age: int                  # 예상 FIRE 달성 나이

    # 기간 계산
    years_to_fire: float           # FIRE까지 남은 년수
    months_to_fire: int            # FIRE까지 남은 개월수

    # 재무 지표
    annual_expense: float          # 연간 지출 (만원)
    safe_withdrawal_amount: float  # 연간 안전 인출액 (4% 룰)
    real_return_rate: float        # 실질 수익률 (수익률 - 인플레이션)

    # 단계별 자산 성장 (5년 단위)
    asset_milestones: list[dict]   # [{"year": 5, "age": 35, "assets": 5000}, ...]

    # AI 로드맵 (프리미엄 전용)
    roadmap: Optional[str] = None


# ── 시나리오 비교 스키마 ──────────────────────────────────────

class ScenarioCompare(BaseModel):
    """시나리오 비교 요청 (프리미엄 전용)"""
    scenarios: list[dict] = Field(
        ...,
        description="비교할 시나리오 목록",
        example=[
            {"name": "공격적", "expected_return_rate": 0.12, "monthly_expense_reduction": 0.2},
            {"name": "보수적", "expected_return_rate": 0.05, "monthly_expense_reduction": 0.0},
        ]
    )


class ScenarioResponse(BaseModel):
    """시나리오 응답"""
    id: int
    name: str
    years_to_fire: float
    fire_amount: float
    monthly_savings: float
    fire_age: int
    assumed_return_rate: float
    assumed_inflation_rate: float
    strategy: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── AI 로드맵 스키마 ──────────────────────────────────────────

class RoadmapRequest(BaseModel):
    """AI 로드맵 생성 요청 (프리미엄 전용)"""
    focus: Optional[str] = Field(
        None,
        description="집중 분야",
        example="지출 절감"  # "지출 절감" | "수입 증대" | "투자 최적화"
    )
    risk_tolerance: str = Field(
        "moderate",
        pattern="^(conservative|moderate|aggressive)$",
        description="투자 성향: conservative/moderate/aggressive"
    )


class RoadmapResponse(BaseModel):
    """AI 로드맵 응답"""
    fire_summary: str       # FIRE 현황 요약
    roadmap: str            # 단계별 로드맵
    action_items: list[str] # 즉시 실행 가능한 액션 아이템
    generated_at: datetime
