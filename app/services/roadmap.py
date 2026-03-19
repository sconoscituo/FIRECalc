from datetime import datetime
from typing import Optional
import google.generativeai as genai
from app.config import settings


class RoadmapGenerator:
    """Gemini AI를 활용한 맞춤 FIRE 달성 로드맵 생성"""

    def __init__(self):
        # Gemini AI 초기화
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    async def generate_roadmap(
        self,
        profile: dict,
        fire_result: dict,
        focus: Optional[str] = None,
        risk_tolerance: str = "moderate",
    ) -> dict:
        """
        Gemini AI로 맞춤 FIRE 달성 로드맵 생성
        - 현재 재무 상황 분석
        - 단계별 실행 계획
        - 즉시 실행 가능한 액션 아이템
        """
        if not self.model:
            return self._fallback_roadmap(profile, fire_result)

        # 투자 성향 한국어 변환
        risk_map = {
            "conservative": "보수적 (안전 자산 위주)",
            "moderate": "중립적 (균형 포트폴리오)",
            "aggressive": "공격적 (성장주/ETF 집중)",
        }
        risk_text = risk_map.get(risk_tolerance, "중립적")
        focus_text = f"집중 분야: {focus}" if focus else "전반적 최적화"

        prompt = f"""
당신은 FIRE(Financial Independence, Retire Early) 전문 재무 코치입니다.
다음 재무 프로필을 분석하고 맞춤 FIRE 달성 로드맵을 제시해주세요.

## 현재 재무 상황
- 나이: {profile['age']}세
- 현재 자산: {profile['current_assets']:,.0f}만원
- 월 수입: {profile['monthly_income']:,.0f}만원
- 월 지출: {profile['monthly_expense']:,.0f}만원
- 월 저축: {fire_result['monthly_savings']:,.0f}만원
- 저축률: {fire_result['monthly_savings'] / profile['monthly_income'] * 100:.1f}%

## FIRE 목표
- FIRE 목표 자산: {fire_result['fire_amount']:,.0f}만원
- 예상 FIRE 달성: {fire_result['years_to_fire']:.1f}년 후 ({fire_result['fire_age']}세)
- 연간 안전 인출액: {fire_result['safe_withdrawal_amount']:,.0f}만원 (4% 룰)
- 적용 수익률: {profile['expected_return_rate'] * 100:.1f}%
- 인플레이션: {profile['inflation_rate'] * 100:.1f}%

## 요청 사항
- 투자 성향: {risk_text}
- {focus_text}

## 응답 형식 (한국어로 작성)

### FIRE 현황 요약
(현재 상황의 강점과 개선점, 3-4문장)

### 단계별 로드맵
**1단계 (현재~3년): 기반 구축**
(구체적인 행동 계획)

**2단계 (3~{max(5, int(fire_result['years_to_fire'])//2)}년): 자산 증식**
(투자 전략 및 수입 증대 방안)

**3단계 ({max(5, int(fire_result['years_to_fire'])//2)}년~FIRE): 가속화**
(포트폴리오 최적화 및 FIRE 준비)

### 즉시 실행 액션 아이템
1. (이번 달 안에 할 수 있는 것)
2. (이번 달 안에 할 수 있는 것)
3. (이번 달 안에 할 수 있는 것)
4. (이번 달 안에 할 수 있는 것)
5. (이번 달 안에 할 수 있는 것)

※ 이 로드맵은 정보 제공 목적이며 투자 권유가 아닙니다.
"""

        try:
            response = await self.model.generate_content_async(prompt)
            full_text = response.text

            # 섹션 파싱
            fire_summary = self._extract_section(full_text, "FIRE 현황 요약")
            roadmap_text = self._extract_roadmap(full_text)
            action_items = self._extract_action_items(full_text)

            return {
                "fire_summary": fire_summary,
                "roadmap": roadmap_text,
                "action_items": action_items,
                "generated_at": datetime.utcnow(),
            }
        except Exception:
            return self._fallback_roadmap(profile, fire_result)

    def _extract_section(self, text: str, section_name: str) -> str:
        """마크다운 섹션 추출"""
        lines = text.split("\n")
        capture = False
        result = []
        for line in lines:
            if section_name in line and ("###" in line or "**" in line):
                capture = True
                continue
            if capture:
                if line.startswith("###") or line.startswith("**단계"):
                    break
                if line.strip():
                    result.append(line.strip())
        return "\n".join(result) if result else "정보를 가져올 수 없습니다."

    def _extract_roadmap(self, text: str) -> str:
        """단계별 로드맵 전체 추출"""
        lines = text.split("\n")
        capture = False
        result = []
        for line in lines:
            if "단계별 로드맵" in line and "###" in line:
                capture = True
                continue
            if capture:
                if "즉시 실행" in line and "###" in line:
                    break
                result.append(line)
        return "\n".join(result).strip() if result else "로드맵 생성에 실패했습니다."

    def _extract_action_items(self, text: str) -> list[str]:
        """즉시 실행 액션 아이템 추출"""
        lines = text.split("\n")
        capture = False
        items = []
        for line in lines:
            if "즉시 실행" in line and "###" in line:
                capture = True
                continue
            if capture and line.strip():
                # 번호로 시작하는 항목 추출
                stripped = line.strip()
                if stripped and stripped[0].isdigit() and "." in stripped[:3]:
                    item = stripped.split(".", 1)[-1].strip()
                    # 괄호 안 설명 제거
                    if item.startswith("(") and item.endswith(")"):
                        item = item[1:-1]
                    if item:
                        items.append(item)
        return items[:5] if items else ["Gemini AI 키를 설정하면 맞춤 액션 아이템을 제공받을 수 있습니다."]

    def _fallback_roadmap(self, profile: dict, fire_result: dict) -> dict:
        """AI 키 미설정 시 기본 로드맵 반환"""
        savings_rate = fire_result["monthly_savings"] / profile["monthly_income"] * 100
        return {
            "fire_summary": (
                f"현재 저축률 {savings_rate:.1f}%로 "
                f"{fire_result['years_to_fire']:.1f}년 후 FIRE 달성 예상입니다. "
                f"AI 로드맵을 이용하려면 GEMINI_API_KEY를 설정하세요."
            ),
            "roadmap": "Gemini AI 키가 설정되지 않아 기본 정보만 제공됩니다.",
            "action_items": [
                "지출 내역을 분석하여 고정비 절감 항목 파악",
                "비상금 3-6개월치 확보 (MMF 또는 CMA 계좌)",
                "인덱스 펀드(S&P 500 ETF) 월 정기 투자 시작",
                "세액공제 혜택이 있는 IRP/연금저축 최대 활용",
                "부업 또는 추가 수입원 탐색",
            ],
            "generated_at": datetime.utcnow(),
        }


# 전역 인스턴스
roadmap_generator = RoadmapGenerator()
