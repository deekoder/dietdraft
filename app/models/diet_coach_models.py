# app/models/diet_coach_models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .common_models import ApiKeyRequest

class DietCoachRequest(ApiKeyRequest):
    """Request model for diet coach conversations."""
    message: str = Field(
        description="User's message to the diet coach",
        example="I want something healthy for dinner with chicken"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID for context"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Optional user ID for session management"
    )

class DietCoachResponse(BaseModel):
    """Response model from diet coach."""
    response: str = Field(description="Diet coach's response")
    action_taken: Optional[str] = Field(description="What action the coach took")
    tools_used: List[str] = Field(description="Which tools were used")
    conversation_id: str = Field(description="Conversation ID for future reference")
    user_id: str = Field(description="User ID for session management")
    data: Optional[Dict[str, Any]] = Field(description="Any structured data returned")
