# app/models/voice_models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from .common_models import ApiKeyRequest

class VoiceInputRequest(ApiKeyRequest):
    """Request model for processing voice input text."""
    voice_text: str = Field(
        description="Raw text transcribed from voice input",
        example="Make me a vegetarian dinner with rice and beans"
    )
    
class VoiceInputResponse(BaseModel):
    """Response model with parsed meal request parameters."""
    meal_type: Optional[str] = None
    include_ingredients: List[str] = []
    dietary_preferences: List[str] = []
    allergies: Optional[List[str]] = []
    max_calories: Optional[int] = None
    cuisine_type: Optional[str] = None
    parsed_text: str = Field(
        description="Human-readable summary of what was understood",
        default=""
    )