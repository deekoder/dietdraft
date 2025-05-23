# app/routes/__init__.py
from app.routes.meal_routes import router as meal_router
from app.routes.reasoning_routes import router as reasoning_router

__all__ = [
    "meal_router",
    "reasoning_router"
]