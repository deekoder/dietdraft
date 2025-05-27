from fastapi import APIRouter, HTTPException
from app.models.diet_coach_models import DietCoachRequest, DietCoachResponse
from app.services.diet_coach_services import process_diet_coach_request

router = APIRouter()

@router.post("/diet-coach", response_model=DietCoachResponse)
async def api_diet_coach(request: DietCoachRequest):
    """
    Your personal AI diet coach for meal planning and nutrition guidance.
    
    The diet coach can:
    - Generate personalized meal recipes
    - Find ingredient substitutions
    - Provide nutritional analysis
    - Remember conversation context
    - Use multiple tools as needed
    """
    try:
        result = process_diet_coach_request(
            message=request.message,
            conversation_id=request.conversation_id,
            api_key=request.api_key
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))