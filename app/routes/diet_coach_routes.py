# app/routes/diet_coach_routes.py
from fastapi import APIRouter, HTTPException
from app.models.diet_coach_models import DietCoachRequest, DietCoachResponse
from app.services.diet_coach_services import process_diet_coach_request

router = APIRouter()

@router.post("/diet-coach", response_model=DietCoachResponse)
async def api_diet_coach(request: DietCoachRequest):
    """
    Your personal diet coach - ask questions, get meal suggestions, and receive 
    personalized nutrition guidance.
    
    The diet coach can:
    - Generate meal recipes based on your preferences
    - Find ingredient substitutions
    - Provide nutritional analysis
    - Answer diet-related questions
    - Remember your conversation context
    
    Example request:
    ```json
    {
      "message": "I want something healthy for dinner with chicken",
      "conversation_id": "optional_id_for_context"
    }
    ```
    """
    try:
        result = process_diet_coach_request(
            message=request.message,
            conversation_id=request.conversation_id,
            user_id=request.user_id,  # Pass user_id to service
            api_key=request.api_key
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))