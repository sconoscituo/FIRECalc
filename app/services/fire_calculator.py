import math
from typing import Optional
from app.config import settings


class FireCalculator:
    """
    FIRE 달성 계산 엔진
    - 4% 룰 (Trinity Study): 연간 지출의 25배 = FIRE 목표 자산
    - 복리 계산: 월 복리 적용
    - 실질 수익률: 명목 수익률 - 인플레이션율
    """

    def calculate_fire_amount(
        self,
        annual_expense: float,
        withdrawal_rate: float = None,
    ) -> float:
        """
        FIRE 목표 자산 계산 (4% 룰 적용)
        - annual_expense: 연간 지출 (만원)
        - withdrawal_rate: 안전 인출율 (기본 4%)
        """
        rate = withdrawal_rate or settings.safe_withdrawal_rate
        return annual_expense / rate

    def calculate_years_to_fire(
        self,
        current_assets: float,
        monthly_savings: float,
        fire_amount: float,
        annual_return_rate: float,
        annual_inflation_rate: float,
    ) -> float:
        """
        FIRE까지 남은 기간(년) 계산
        - 월 복리 적용, 실질 수익률(명목 - 인플레이션) 기준
        """
        # 실질 수익률 계산 (Fisher 방정식)
        real_return_rate = (1 + annual_return_rate) / (1 + annual_inflation_rate) - 1
        monthly_rate = (1 + real_return_rate) ** (1 / 12) - 1

        # 이미 FIRE 달성한 경우
        if current_assets >= fire_amount:
            return 0.0

        # 저축이 없는 경우 (수입 <= 지출)
        if monthly_savings <= 0:
            if monthly_rate <= 0:
                return float("inf")
            # 자산 성장만으로 달성 가능한지 확인
            if current_assets <= 0:
                return float("inf")
            years = math.log(fire_amount / current_assets) / math.log(1 + real_return_rate)
            return max(0.0, years)

        # 복리 + 정기 적립 공식
        # FV = PV * (1+r)^n + PMT * ((1+r)^n - 1) / r
        # fire_amount = current_assets * (1+r)^n + monthly_savings * ((1+r)^n - 1) / r
        # 수치 해석으로 n 계산 (이진 탐색)
        if monthly_rate == 0:
            # 수익률 0인 경우 단순 계산
            months = (fire_amount - current_assets) / monthly_savings
            return max(0.0, months / 12)

        low, high = 0.0, 100.0  # 최대 100년
        for _ in range(100):  # 충분한 반복으로 수렴
            mid = (low + high) / 2
            n = mid * 12  # 개월 수
            fv = current_assets * (1 + monthly_rate) ** n + monthly_savings * (
                ((1 + monthly_rate) ** n - 1) / monthly_rate
            )
            if fv >= fire_amount:
                high = mid
            else:
                low = mid
            if high - low < 0.001:
                break

        return round((low + high) / 2, 2)

    def calculate_asset_milestones(
        self,
        current_assets: float,
        monthly_savings: float,
        annual_return_rate: float,
        annual_inflation_rate: float,
        years_to_fire: float,
        current_age: int,
        step_years: int = 5,
    ) -> list[dict]:
        """
        연도별 자산 성장 시뮬레이션 (5년 단위)
        """
        real_return_rate = (1 + annual_return_rate) / (1 + annual_inflation_rate) - 1
        monthly_rate = (1 + real_return_rate) ** (1 / 12) - 1

        milestones = []
        total_years = math.ceil(years_to_fire) + 1

        for year in range(0, total_years + 1, step_years):
            n = year * 12
            if monthly_rate == 0:
                assets = current_assets + monthly_savings * n
            else:
                assets = current_assets * (1 + monthly_rate) ** n + monthly_savings * (
                    ((1 + monthly_rate) ** n - 1) / monthly_rate
                )
            milestones.append({
                "year": year,
                "age": current_age + year,
                "assets": round(assets, 2),
            })

        return milestones

    def calculate_full(
        self,
        age: int,
        current_assets: float,
        monthly_income: float,
        monthly_expense: float,
        expected_return_rate: float,
        inflation_rate: float,
        target_amount: Optional[float] = None,
    ) -> dict:
        """전체 FIRE 계산 실행 - 모든 결과 반환"""
        monthly_savings = monthly_income - monthly_expense
        annual_expense = monthly_expense * 12
        annual_savings = monthly_savings * 12

        # FIRE 목표 자산 (입력값 또는 4% 룰 자동 계산)
        fire_amount = target_amount or self.calculate_fire_amount(annual_expense)

        # FIRE까지 남은 기간
        years_to_fire = self.calculate_years_to_fire(
            current_assets=current_assets,
            monthly_savings=monthly_savings,
            fire_amount=fire_amount,
            annual_return_rate=expected_return_rate,
            annual_inflation_rate=inflation_rate,
        )

        # 실질 수익률
        real_return_rate = (1 + expected_return_rate) / (1 + inflation_rate) - 1

        # 자산 성장 마일스톤
        milestones = self.calculate_asset_milestones(
            current_assets=current_assets,
            monthly_savings=monthly_savings,
            annual_return_rate=expected_return_rate,
            annual_inflation_rate=inflation_rate,
            years_to_fire=years_to_fire,
            current_age=age,
        )

        return {
            "current_assets": current_assets,
            "monthly_savings": monthly_savings,
            "annual_savings": annual_savings,
            "fire_amount": round(fire_amount, 2),
            "fire_age": age + int(years_to_fire),
            "years_to_fire": years_to_fire,
            "months_to_fire": int(years_to_fire * 12),
            "annual_expense": annual_expense,
            "safe_withdrawal_amount": round(fire_amount * settings.safe_withdrawal_rate, 2),
            "real_return_rate": round(real_return_rate, 4),
            "asset_milestones": milestones,
        }


# 전역 인스턴스
fire_calculator = FireCalculator()
