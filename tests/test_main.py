import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    """테스트용 비동기 HTTP 클라이언트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    """헬스체크 엔드포인트 테스트"""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client):
    """루트 엔드포인트 테스트"""
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "FIRECalc"


@pytest.mark.asyncio
async def test_register_and_login(client):
    """회원가입 및 로그인 흐름 테스트"""
    resp = await client.post("/users/register", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert resp.status_code == 201
    assert resp.json()["is_premium"] is False

    resp = await client.post("/users/login", data={
        "username": "test@example.com",
        "password": "testpass123"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_fire_calculation(client):
    """FIRE 계산 전체 흐름 테스트"""
    # 회원가입 + 로그인
    await client.post("/users/register", json={"email": "fire@example.com", "password": "pass123"})
    login = await client.post("/users/login", data={"username": "fire@example.com", "password": "pass123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 프로필 생성
    resp = await client.post("/calculator/profile", json={
        "age": 30,
        "current_assets": 5000.0,
        "monthly_income": 500.0,
        "monthly_expense": 300.0,
        "expected_return_rate": 0.07,
        "inflation_rate": 0.03,
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["monthly_savings"] == 200.0

    # FIRE 계산
    resp = await client.post("/calculator/calculate", headers=headers)
    assert resp.status_code == 200
    result = resp.json()
    assert result["fire_amount"] > 0
    assert result["years_to_fire"] > 0
    assert result["fire_age"] >= 30
    assert len(result["asset_milestones"]) > 0


@pytest.mark.asyncio
async def test_fire_calculator_math():
    """FIRE 계산 수학 로직 단위 테스트"""
    from app.services.fire_calculator import FireCalculator

    calc = FireCalculator()

    # 4% 룰: 연간 지출 2400만원 -> 목표 자산 6억
    fire_amount = calc.calculate_fire_amount(annual_expense=2400.0)
    assert abs(fire_amount - 60000.0) < 1.0  # 2400 / 0.04 = 60000

    # 이미 FIRE 달성한 경우 0년 반환
    years = calc.calculate_years_to_fire(
        current_assets=100000.0,
        monthly_savings=200.0,
        fire_amount=60000.0,
        annual_return_rate=0.07,
        annual_inflation_rate=0.03,
    )
    assert years == 0.0


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    """인증 없이 보호된 엔드포인트 접근 시 401 테스트"""
    resp = await client.get("/calculator/profile")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_premium_only_roadmap(client):
    """무료 사용자의 로드맵 접근 차단 테스트"""
    await client.post("/users/register", json={"email": "free@example.com", "password": "pass"})
    login = await client.post("/users/login", data={"username": "free@example.com", "password": "pass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/calculator/roadmap", json={"risk_tolerance": "moderate"}, headers=headers)
    assert resp.status_code == 403
