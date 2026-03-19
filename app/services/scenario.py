from datetime import datetime
from typing import Optional
import google.generativeai as genai
from app.config import settings


class ScenarioAnalyzer:
    """
    FIRE 시나리오 비교 분석 + 인플레이션 조정 계산 엔진
    - 복수 시나리오 동시 비교
    - 4% 룰 + 인플레이션 조정 FIRE 목표 자산 계산
    - Gemini AI 시나리오 조언
    """

    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    def calculate_fire(
        self,
        current_age: int,
        current_savings: float,
        monthly_savings: float,
        expected_return: float,
        target_expenses: float,
        inflation_rate: float = 0.03,
    ) -> dict:
        """
        FIRE 숫자 계산 (4% 룰 + 인플레이션 조정)
        - target_expenses: 연간 목표 지출 (만원)
        - 인플레이션을 10년 복리로 반영하여 미래 생활비 보정
        """
        # 인플레이션 조정 FIRE 목표: 연지출 × 25 × (1 + 인플레이션)^10
        fire_number = target_expenses * 25 * (1 + inflation_rate) ** 10

        # 월 복리 수익률
        monthly_rate = (1 + expected_return) ** (1 / 12) - 1

        years = 0
        savings = current_savings

        if savings >= fire_number:
            return {
                "fire_number": round(fire_number, 2),
                "years_to_fire": 0,
                "fire_age": current_age,
                "final_savings": round(savings, 2),
                "monthly_savings": monthly_savings,
                "inflation_adjusted": True,
            }

        # 연도별 시뮬레이션 (최대 100년)
        while savings < fire_number and years < 100:
            if monthly_rate == 0:
                savings = savings + monthly_savings * 12
            else:
                # 1년치 복리 성장 + 월 적립
                savings = (
                    savings * (1 + monthly_rate) ** 12
                    + monthly_savings * (((1 + monthly_rate) ** 12 - 1) / monthly_rate)
                )
            years += 1

        return {
            "fire_number": round(fire_number, 2),
            "years_to_fire": years,
            "fire_age": current_age + years,
            "final_savings": round(savings, 2),
            "monthly_savings": monthly_savings,
            "inflation_adjusted": True,
        }

    def compare_scenarios(self, scenarios: list) -> dict:
        """
        여러 FIRE 시나리오 비교 분석 (최대 3개)
        각 시나리오는 calculate_fire 파라미터를 포함한 dict
        """
        if len(scenarios) > 3:
            scenarios = scenarios[:3]

        results = []
        for idx, s in enumerate(scenarios):
            result = self.calculate_fire(
                current_age=s["current_age"],
                current_savings=s["current_savings"],
                monthly_savings=s["monthly_savings"],
                expected_return=s["expected_return"],
                target_expenses=s["target_expenses"],
                inflation_rate=s.get("inflation_rate", 0.03),
            )
            entry = {
                "scenario_index": idx + 1,
                "name": s.get("name", f"시나리오 {idx + 1}"),
                **s,
                **result,
            }
            results.append(entry)

        # FIRE 달성이 가능한 시나리오 중 가장 빠른 것
        reachable = [r for r in results if r["years_to_fire"] < 100]
        best = min(reachable, key=lambda x: x["years_to_fire"]) if reachable else results[0]

        # 차트용 비교 데이터
        chart_data = [
            {
                "name": r["name"],
                "years_to_fire": r["years_to_fire"],
                "fire_age": r["fire_age"],
                "fire_number": r["fire_number"],
                "final_savings": r["final_savings"],
            }
            for r in results
        ]

        return {
            "scenarios": results,
            "best_scenario": best,
            "comparison_chart_data": chart_data,
            "total_compared": len(results),
        }

    async def ai_advice(self, scenario_result: dict) -> str:
        """
        시나리오 결과에 대한 Gemini AI 조언
        - AI 키 미설정 시 기본 조언 반환
        """
        if not self.model:
            return self._fallback_advice(scenario_result)

        scenarios_text = ""
        for s in scenario_result.get("scenarios", []):
            scenarios_text += (
                f"\n- {s['name']}: "
                f"FIRE 목표 {s['fire_number']:,.0f}만원, "
                f"{s['years_to_fire']}년 후 달성 (만 {s['fire_age']}세), "
                f"월 저축 {s['monthly_savings']:,.0f}만원"
            )

        best = scenario_result.get("best_scenario", {})
        prompt = f"""
당신은 FIRE(Financial Independence, Retire Early) 전문 재무 코치입니다.
아래 시나리오 비교 결과를 분석하고 간결한 조언을 한국어로 제공하세요.

## 시나리오 비교 결과 ({scenario_result.get('total_compared', 0)}개)
{scenarios_text}

## 최적 시나리오
- {best.get('name', 'N/A')}: {best.get('years_to_fire', 'N/A')}년 후 FIRE (만 {best.get('fire_age', 'N/A')}세)

## 요청
1. 각 시나리오의 핵심 차이점 분석 (2-3문장)
2. 최적 시나리오 선택 이유 (1-2문장)
3. 실행 가능한 개선 조언 3가지 (번호 목록)

간결하고 실용적으로 작성하세요. 투자 권유가 아닌 정보 제공임을 명시하세요.
"""
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception:
            return self._fallback_advice(scenario_result)

    def _fallback_advice(self, scenario_result: dict) -> str:
        """AI 키 미설정 또는 오류 시 기본 조언"""
        best = scenario_result.get("best_scenario", {})
        return (
            f"최적 시나리오 '{best.get('name', 'N/A')}'에서 "
            f"{best.get('years_to_fire', 'N/A')}년 후 FIRE 달성이 예상됩니다. "
            f"인플레이션 조정 FIRE 목표는 {best.get('fire_number', 0):,.0f}만원입니다. "
            "AI 맞춤 조언을 받으려면 GEMINI_API_KEY를 설정하세요. "
            "일반 조언: 저축률을 높이고, 분산 투자를 유지하며, "
            "세액공제 혜택(IRP/연금저축)을 최대한 활용하세요."
        )


# 전역 인스턴스
scenario_analyzer = ScenarioAnalyzer()
