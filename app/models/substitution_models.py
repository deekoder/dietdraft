from pydantic import BaseModel, Field
from typing import List, Optional
from .common_models import ApiKeyRequest

class SubstitutionRequest(ApiKeyRequest):
    """Request model for finding ingredient substitutions."""
    original_ingredient: str = Field(
        description="The ingredient to find substitutions for",
        example="heavy cream"
    )
    reason: str = Field(
        description="Reason for substitution (dairy-free, lower-calorie, allergy, etc.)",
        example="dairy-free"
    )
    recipe_context: Optional[str] = Field(
        default=None,
        description="Optional context about how the ingredient is used",
        example="creamy pasta sauce"
    )

class SubstitutionOption(BaseModel):
    """A single substitution option."""
    ingredient: str = Field(description="Substitute ingredient name")
    notes: str = Field(description="Usage notes and tips")

class SubstitutionResponse(BaseModel):
    """Response model with substitution alternatives."""
    original_ingredient: str
    reason: str
    substitutions: List[SubstitutionOption]