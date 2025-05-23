# app/routes/meal_routes.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# Import models
from app.models.meal_models import MealRequest, MealResponse

# Import services
from app.services.meal_service import generate_meal

# Create router
router = APIRouter()

@router.post("/generate-meal", response_model=MealResponse)
async def api_generate_meal(request: MealRequest):
    """
    Generate a customized meal recipe based on preferences.
    
    This endpoint creates a meal recipe with the specified parameters such as meal type, 
    dietary preferences, allergies, and desired ingredients.
    
    Example request:
    ```json
    {
      "meal_type": "dinner",
      "include_ingredients": ["chicken", "broccoli"],
      "dietary_preferences": ["high-protein", "low-carb"],
      "allergies": ["nuts"]
    }
    ```
    """
    try:
        result = generate_meal(
            api_key=request.api_key,
            meal_type=request.meal_type,
            dietary_preferences=request.dietary_preferences,
            allergies=request.allergies,
            max_calories=request.max_calories,
            cuisine_type=request.cuisine_type,
            include_ingredients=request.include_ingredients
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))