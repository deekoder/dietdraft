# models/meal_models.py
from pydantic import BaseModel
from typing import List
from .common_models import ApiKeyRequest

class MealRequest(ApiKeyRequest):
    """Request model for generating a single meal."""
    pass

class MealResponse(BaseModel):
    """Response model for a generated meal."""
    meal_name: str
    ingredients: List[str]
    instructions: str