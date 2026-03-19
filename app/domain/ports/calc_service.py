"""
헥사고날 아키텍처 - FIRECalc Service Port
FIRE 계산 도메인 서비스 추상 인터페이스
"""
from abc import abstractmethod
from typing import Any, Dict, List

from .base_service import AbstractService


class AbstractFIRECalcService(AbstractService):
    """FIRE 계산 서비스 포트 - 구현체는 이 인터페이스를 따라야 함"""

    @abstractmethod
    async def calculate_fire_number(
        self,
        annual_expense: float,
        withdrawal_rate: float = 0.04,
    ) -> Dict[str, Any]:
        """
        FIRE 목표 자산 계산 (4% 룰 기반)
        :param annual_expense: 연간 지출액
        :param withdrawal_rate: 안전 인출률 (기본 4%)
        :return: FIRE 목표 금액 및 관련 지표
        """
        ...

    @abstractmethod
    async def project_timeline(
        self,
        current_savings: float,
        monthly_savings: float,
        fire_number: float,
        annual_return: float,
    ) -> Dict[str, Any]:
        """
        FIRE 달성까지 예상 기간 계산
        :param current_savings: 현재 저축액
        :param monthly_savings: 월 저축액
        :param fire_number: FIRE 목표 금액
        :param annual_return: 연간 기대 수익률
        :return: 달성 예상 연월 및 단계별 자산 성장 데이터
        """
        ...

    @abstractmethod
    async def simulate_scenarios(
        self,
        base_params: Dict[str, Any],
        scenarios: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        다양한 시나리오별 FIRE 시뮬레이션
        :param base_params: 기본 입력 파라미터
        :param scenarios: 시나리오 목록 (지출 변화, 수익률 변화 등)
        :return: 시나리오별 FIRE 달성 분석 결과
        """
        ...
