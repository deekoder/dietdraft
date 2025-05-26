# app/models/__init__.py
from .common_models import ApiKeyRequest, ErrorResponse
from .meal_models import MealRequest, MealResponse
from .reasoning_models import ReasoningRequest, ReasoningResponse, ReasoningHighlights
from .voice_models import VoiceInputRequest, VoiceInputResponse  # Add this line

__all__ = [
    "ApiKeyRequest",
    "ErrorResponse",
    "MealRequest",
    "MealResponse",
    "ReasoningRequest",
    "ReasoningResponse",
    "ReasoningHighlights",
    "VoiceInputRequest",     
    "VoiceInputResponse"     
]