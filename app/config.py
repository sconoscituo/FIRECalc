from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 앱 기본 설정
    app_name: str = "FIRECalc"
    debug: bool = False

    # 데이터베이스
    database_url: str = "sqlite+aiosqlite:///./firecalc.db"

    # JWT 인증
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7일

    # Google Gemini AI
    gemini_api_key: str = ""

    # FIRE 계산 기본값
    default_inflation_rate: float = 0.03      # 연 3% 인플레이션
    default_expected_return: float = 0.07     # 연 7% 수익률 (S&P 500 장기 평균)
    safe_withdrawal_rate: float = 0.04        # 4% 룰 (Trinity Study)

    class Config:
        env_file = ".env"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()
