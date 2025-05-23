# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import from our modules
from .models import MealRequest, MealResponse
from .models import ReasoningRequest, ReasoningResponse
from .services import generate_meal, generate_meal_reasoning

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="DietDraft API",
    description="Simple API for generating meals",
    version="0.1.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the DietDraft API",
        "endpoints": {
            "POST /generate-meal": "Generate a single meal recipe with customizable options"
        },
        "version": "0.1.0"
    }

@app.post("/generate-meal", response_model=MealResponse)
async def api_generate_meal(request: MealRequest):
    """Generate a single meal with dietary preferences and meal type."""
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
    
# main.py

@app.post("/meal-reasoning", response_model=ReasoningResponse)
async def api_meal_reasoning(request: ReasoningRequest):
    """
    Generate nutritional reasoning about a meal.
    
    This endpoint analyzes a meal's ingredients and provides concise nutritional insights
    organized into three key areas:
    
    - Key ingredient choices: Why specific ingredients were selected
    - Nutritional benefits: Overall nutritional value of the meal
    - Dietary alignment: How the meal meets specified dietary preferences
    
    The response contains brief, evidence-based explanations suitable for educational
    display alongside a recipe.
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