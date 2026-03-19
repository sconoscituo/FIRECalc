from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"   # 월 4,900원

PLAN_LIMITS = {
    PlanType.FREE: {"scenarios": 2,  "ai_roadmap": False, "portfolio_analysis": False},
    PlanType.PRO:  {"scenarios": 20, "ai_roadmap": True,  "portfolio_analysis": True},
}
PLAN_PRICES_KRW = {PlanType.FREE: 0, PlanType.PRO: 4900}
