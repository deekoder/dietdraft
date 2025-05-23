# models/__init__.py
from .meal_models import MealRequest, MealResponse
from .common_models import ApiKeyRequest, ErrorResponse

__all__ = [
    "MealRequest",
    "MealResponse", 
    "ApiKeyRequest",
    "ErrorResponse"
]