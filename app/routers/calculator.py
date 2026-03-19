from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.profile import FinancialProfile
from app.models.scenario import FireScenario
from app.schemas.fire import (
    ProfileCreate, ProfileResponse, FireResult,
    ScenarioCompare, ScenarioResponse, RoadmapRequest, RoadmapResponse
)
from app.utils.auth import get_current_user, get_premium_user
from app.services.fire_calculator import fire_calculator
from app.services.roadmap import roadmap_generator
from app.config import settings

router = APIRouter(prefix="/calculator", tags=["FIRE 계산기"])


@router.post("/profile", response_model=ProfileResponse)
async def upsert_profile(
    profile_in: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """재무 프로필 생성 또는 수정 (1인 1프로필)"""
    result = await db.execute(
        select(FinancialProfile).where(FinancialProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if profile:
        # 기존 프로필 수정
        for field, value in profile_in.model_dump().items():
            setattr(profile, field, value)
    else:
        # 신규 프로필 생성
        profile = FinancialProfile(user_id=current_user.id, **profile_in.model_dump())
        db.add(profile)

    await db.flush()
    await db.refresh(profile)

    monthly_savings = profile.monthly_income - profile.monthly_expense
    return ProfileResponse(
        id=profile.id,
        age=profile.age,
        current_assets=profile.current_assets,
        monthly_income=profile.monthly_income,
        monthly_expense=profile.monthly_expense,
        monthly_savings=monthly_savings,
        target_amount=profile.target_amount,
        expected_return_rate=profile.expected_return_rate,
        inflation_rate=profile.inflation_rate,
        created_at=profile.created_at,
    )


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """내 재무 프로필 조회"""
    result = await db.execute(
        select(FinancialProfile).where(FinancialProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="재무 프로필이 없습니다. 먼저 프로필을 생성하세요.")

    monthly_savings = profile.monthly_income - profile.monthly_expense
    return ProfileResponse(
        id=profile.id,
        age=profile.age,
        current_assets=profile.current_assets,
        monthly_income=profile.monthly_income,
        monthly_expense=profile.monthly_expense,
        monthly_savings=monthly_savings,
        target_amount=profile.target_amount,
        expected_return_rate=profile.expected_return_rate,
        inflation_rate=profile.inflation_rate,
        created_at=profile.created_at,
    )


@router.post("/calculate", response_model=FireResult)
async def calculate_fire(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FIRE 달성 기간 계산 (저장된 프로필 기반)"""
    result = await db.execute(
        select(FinancialProfile).where(FinancialProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="재무 프로필이 없습니다. 먼저 /calculator/profile 에서 프로필을 생성하세요.")

    calc_result = fire_calculator.calculate_full(
        age=profile.age,
        current_assets=profile.current_assets,
        monthly_income=profile.monthly_income,
        monthly_expense=profile.monthly_expense,
        expected_return_rate=profile.expected_return_rate,
        inflation_rate=profile.inflation_rate,
        target_amount=profile.target_amount,
    )
    return FireResult(**calc_result)


@router.post("/scenarios", response_model=list[ScenarioResponse])
async def compare_scenarios(
    scenario_req: ScenarioCompare,
    current_user: User = Depends(get_premium_user),  # 프리미엄 전용
    db: AsyncSession = Depends(get_db),
):
    """여러 시나리오 비교 분석 (프리미엄 전용)"""
    profile_result = await db.execute(
        select(FinancialProfile).where(FinancialProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="재무 프로필이 없습니다.")

    saved_scenarios = []
    for sc in scenario_req.scenarios:
        # 시나리오별 파라미터 적용
        return_rate = sc.get("expected_return_rate", profile.expected_return_rate)
        expense_reduction = sc.get("monthly_expense_reduction", 0.0)
        adjusted_expense = profile.monthly_expense * (1 - expense_reduction)

        calc = fire_calculator.calculate_full(
            age=profile.age,
            current_assets=profile.current_assets,
            monthly_income=profile.monthly_income,
            monthly_expense=adjusted_expense,
            expected_return_rate=return_rate,
            inflation_rate=profile.inflation_rate,
            target_amount=profile.target_amount,
        )

        scenario = FireScenario(
            user_id=current_user.id,
            name=sc.get("name", "시나리오"),
            years_to_fire=calc["years_to_fire"],
            fire_amount=calc["fire_amount"],
            monthly_savings=calc["monthly_savings"],
            fire_age=calc["fire_age"],
            assumed_return_rate=return_rate,
            assumed_inflation_rate=profile.inflation_rate,
        )
        db.add(scenario)
        saved_scenarios.append(scenario)

    await db.flush()
    for s in saved_scenarios:
        await db.refresh(s)

    return saved_scenarios


@router.get("/scenarios", response_model=list[ScenarioResponse])
async def get_scenarios(
    current_user: User = Depends(get_premium_user),  # 프리미엄 전용
    db: AsyncSession = Depends(get_db),
):
    """저장된 시나리오 목록 조회 (프리미엄 전용)"""
    result = await db.execute(
        select(FireScenario).where(FireScenario.user_id == current_user.id)
        .order_by(FireScenario.created_at.desc())
    )
    return result.scalars().all()


@router.post("/roadmap", response_model=RoadmapResponse)
async def generate_roadmap(
    roadmap_req: RoadmapRequest,
    current_user: User = Depends(get_premium_user),  # 프리미엄 전용
    db: AsyncSession = Depends(get_db),
):
    """Gemini AI 맞춤 FIRE 달성 로드맵 생성 (프리미엄 전용)"""
    profile_result = await db.execute(
        select(FinancialProfile).where(FinancialProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="재무 프로필이 없습니다.")

    # FIRE 계산 실행
    calc = fire_calculator.calculate_full(
        age=profile.age,
        current_assets=profile.current_assets,
        monthly_income=profile.monthly_income,
        monthly_expense=profile.monthly_expense,
        expected_return_rate=profile.expected_return_rate,
        inflation_rate=profile.inflation_rate,
        target_amount=profile.target_amount,
    )

    profile_dict = {
        "age": profile.age,
        "current_assets": profile.current_assets,
        "monthly_income": profile.monthly_income,
        "monthly_expense": profile.monthly_expense,
        "expected_return_rate": profile.expected_return_rate,
        "inflation_rate": profile.inflation_rate,
    }

    result = await roadmap_generator.generate_roadmap(
        profile=profile_dict,
        fire_result=calc,
        focus=roadmap_req.focus,
        risk_tolerance=roadmap_req.risk_tolerance,
    )
    return RoadmapResponse(**result)
