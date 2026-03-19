from datetime import datetime
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class FireScenario(Base):
    """FIRE 시나리오 모델 - 다양한 전략 시뮬레이션 결과 저장"""
    __tablename__ = "fire_scenarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 사용자 연결
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 시나리오 기본 정보
    name: Mapped[str] = mapped_column(String(100), nullable=False)        # 예: "공격적 투자", "보수적 안전"

    # 계산 결과
    years_to_fire: Mapped[float] = mapped_column(Float, nullable=False)   # FIRE까지 남은 년수
    fire_amount: Mapped[float] = mapped_column(Float, nullable=False)     # FIRE 목표 자산 (만원)
    monthly_savings: Mapped[float] = mapped_column(Float, nullable=False) # 필요 월 저축액 (만원)
    fire_age: Mapped[int] = mapped_column(Integer, nullable=False)        # 예상 FIRE 나이

    # 시나리오 파라미터
    assumed_return_rate: Mapped[float] = mapped_column(Float, nullable=False)   # 적용 수익률
    assumed_inflation_rate: Mapped[float] = mapped_column(Float, nullable=False) # 적용 인플레이션

    # AI 전략 (프리미엄 전용)
    strategy: Mapped[str | None] = mapped_column(Text, nullable=True)     # Gemini AI 생성 전략

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="scenarios")

    def __repr__(self) -> str:
        return f"<FireScenario id={self.id} name={self.name} years={self.years_to_fire}>"
