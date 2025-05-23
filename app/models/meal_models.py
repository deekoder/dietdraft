# models/meal_models.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from .common_models import ApiKeyRequest

class MealRequest(ApiKeyRequest):
    """Request model for generating a single meal."""
    meal_type: Optional[str] = Field(
        default=None,
        description="Type of meal to generate (breakfast, lunch, dinner, snack, dessert)",
        example="breakfast"
    )
    include_ingredients: Optional[List[str]] = Field(
        default=[],
        description="List of ingredients to try to include in the meal (up to 5)",
        example=["chicken breast", "broccoli", "rice"],
        max_items=5
    )
    dietary_preferences: Optional[List[str]] = Field(
        default=[],
        description="List of dietary preferences and specializations (e.g., 'vegetarian', 'keto', 'pre-diabetic')",
        example=["vegetarian", "pre-diabetic"]
    )
    allergies: Optional[List[str]] = Field(
        default=[],
        description="List of food allergies to avoid",
        example=["nuts", "shellfish"]
    )
    max_calories: Optional[int] = Field(
        default=None,
        description="Maximum calories per serving",
        gt=0,
        le=2000,
        example=500
    )
    cuisine_type: Optional[str] = Field(
        default=None,
        description="Preferred cuisine type",
        example="Mediterranean"
    )

    @validator('meal_type')
    def validate_meal_type(cls, v):
        if v is None:
            return v
        allowed_types = ["breakfast", "lunch", "dinner", "snack", "dessert"]
        if v.lower() not in allowed_types:
            raise ValueError(f"meal_type must be one of: {', '.join(allowed_types)}")
        return v.lower()

    @validator('include_ingredients')
    def validate_include_ingredients(cls, v):
        if v is None:
            return []
        if len(v) > 5:
            raise ValueError("include_ingredients cannot have more than 5 items")
        # Clean up ingredient names (strip whitespace, basic validation)
        cleaned = [ingredient.strip() for ingredient in v if ingredient.strip()]
        return cleaned

class MealResponse(BaseModel):
    """Response model for a generated meal."""
    meal_name: str
    ingredients: List[str]
    instructions: str
    estimated_calories: Optional[int] = None
    dietary_info: Optional[str] = None