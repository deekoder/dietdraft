# models/common_models.py
from pydantic import BaseModel
from typing import Optional

class ApiKeyRequest(BaseModel):
    """Base request model with optional API key."""
    api_key: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    detail: Optional[str] = None