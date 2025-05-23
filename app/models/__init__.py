# models/__init__.py
from .meal_models import MealRequest, MealResponse
from .reasoning_models import ReasoningRequest, ReasoningResponse
from .common_models import ApiKeyRequest, ErrorResponse

__all__ = [
    "MealRequest",
    "MealResponse", 
    "ApiKeyRequest",
    "ReasoningRequest",
    "ReasoningResponse",
    "ErrorResponse"
]