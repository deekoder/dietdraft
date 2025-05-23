# app/routes/reasoning_routes.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# Import models
from app.models.reasoning_models import ReasoningRequest, ReasoningResponse

# Import services
from app.services.reasoning_services import generate_meal_reasoning

# Create router
router = APIRouter()

@router.post("/meal-reasoning", response_model=ReasoningResponse)
async def api_meal_reasoning(request: ReasoningRequest):
    """
    Get nutritional reasoning about a meal.
    
    This endpoint analyzes a meal based on its name, ingredients, and optionally instructions,
    providing concise nutritional insights organized into three key areas.
    
    Example request:
    ```json
    {
      "meal_name": "Mediterranean Quinoa Bowl",
      "ingredients": [
        "1 cup cooked quinoa",
        "1/2 cup chickpeas",
        "1/4 cup cucumber",
        "2 tbsp feta cheese",
        "1 tbsp olive oil"
      ],
      "dietary_preferences": ["vegetarian", "mediterranean"]
    }
    ```
    """
    try:
        result = generate_meal_reasoning(
            api_key=request.api_key,
            meal_name=request.meal_name,
            ingredients=request.ingredients,
            instructions=request.instructions,
            dietary_preferences=request.dietary_preferences
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))