# app/routes/__init__.py
from app.routes.meal_routes import router as meal_router
from app.routes.reasoning_routes import router as reasoning_router
from app.routes.diet_coach_routes import router as diet_coach_router

__all__ = [
    "meal_router",
    "reasoning_router",
    "voice_router",
    "substitution_router",
    "diet_coact_router"
]