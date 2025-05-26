
# app/routes/voice_routes.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# Import models
from app.models.voice_models import VoiceInputRequest, VoiceInputResponse

# Import service
from app.services.voice_parser_service import parse_voice_to_json

# Create router
router = APIRouter()

@router.post("/parse-voice", response_model=VoiceInputResponse)
async def api_parse_voice(request: VoiceInputRequest):
    """
    Parse voice input text into structured meal parameters using an LLM.
    
    This endpoint takes raw text transcribed from voice input and uses an LLM
    to extract meal type, ingredients, dietary preferences, and other parameters
    needed for generating a recipe.
    
    Example request:
    ```json
    {
      "voice_text": "Make me a vegetarian dinner with rice and beans"
    }
    ```
    """
    try:
        if not request.voice_text:
            raise ValueError("Voice text cannot be empty")
        
        # Parse the voice input using LLM
        result = parse_voice_to_json(
            voice_text=request.voice_text,
            api_key=request.api_key
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))