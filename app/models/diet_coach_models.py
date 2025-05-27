from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .common_models import ApiKeyRequest

class DietCoachRequest(ApiKeyRequest):
    message: str = Field(description="User's message to the diet coach")
    conversation_id: Optional[str] = Field(default=None, description="Optional conversation ID")

class DietCoachResponse(BaseModel):
    response: str = Field(description="Diet coach's response")
    action_taken: Optional[str] = Field(description="What action the coach took")
    tools_used: List[str] = Field(description="Which tools were used")
    conversation_id: str = Field(description="Conversation ID for future reference")
    data: Optional[Dict[str, Any]] = Field(description="Any structured data returned")