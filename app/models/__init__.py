# app/models/__init__.py
from .common_models import ApiKeyRequest, ErrorResponse
from .meal_models import MealRequest, MealResponse
from .reasoning_models import ReasoningRequest, ReasoningResponse, ReasoningHighlights
from .voice_models import VoiceInputRequest, VoiceInputResponse  
from .substitution_models import SubstitutionOption, SubstitutionRequest, SubstitutionResponse
from .diet_coach_models import DietCoachRequest, DietCoachResponse

__all__ = [
    "ApiKeyRequest",
    "ErrorResponse",
    "MealRequest",
    "MealResponse",
    "ReasoningRequest",
    "ReasoningResponse",
    "ReasoningHighlights",
    "VoiceInputRequest",     
    "VoiceInputResponse",
    "SubstitutionRequest",
    "SubstitutionResponse",
    "DietCoachRequest",
    "DietCoachResponse"

]