from datetime import datetime
from sqlalchemy import Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class FinancialProfile(Base):
    """사용자 재무 프로필 모델"""
    __tablename__ = "financial_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 사용자 연결 (1:1 관계)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # 기본 재무 정보
    age: Mapped[int] = mapped_column(Integer, nullable=False)                         # 현재 나이
    current_assets: Mapped[float] = mapped_column(Float, nullable=False)              # 현재 총 자산 (만원)
    monthly_income: Mapped[float] = mapped_column(Float, nullable=False)              # 월 수입 (만원)
    monthly_expense: Mapped[float] = mapped_column(Float, nullable=False)             # 월 지출 (만원)

    # FIRE 목표 설정
    target_amount: Mapped[float | None] = mapped_column(Float, nullable=True)         # FIRE 목표 자산 (미입력 시 4% 룰로 자동 계산)
    expected_return_rate: Mapped[float] = mapped_column(Float, default=0.07)          # 연 기대 수익률 (기본 7%)
    inflation_rate: Mapped[float] = mapped_column(Float, default=0.03)               # 연 인플레이션율 (기본 3%)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<FinancialProfile user_id={self.user_id} age={self.age} assets={self.current_assets}>"
