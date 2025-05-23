# models/reasoning_models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from .common_models import ApiKeyRequest

class ReasoningRequest(ApiKeyRequest):
    """Request model for generating reasoning about a meal."""
    meal_name: str = Field(
        description="Name of the meal to explain"
    )
    ingredients: List[str] = Field(
        description="List of ingredients in the meal"
    )
    instructions: Optional[str] = Field(
        default=None,
        description="Cooking instructions for the meal"
    )
    dietary_preferences: Optional[List[str]] = Field(
        default=None,
        description="Dietary preferences that should be addressed"
    )
    
class ReasoningHighlights(BaseModel):
    """Minimalistic reasoning highlights for a meal."""
    key_ingredient_choices: str = Field(
        description="Brief explanation of key ingredient selections"
    )
    nutritional_benefits: str = Field(
        description="Key nutritional benefits of the meal"
    )
    dietary_alignment: str = Field(
        description="How the meal meets specified dietary requirements"
    )

class ReasoningResponse(BaseModel):
    """Response model for meal reasoning."""
    meal_name: str
    reasoning: ReasoningHighlights