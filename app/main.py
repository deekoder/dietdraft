# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import from our modules
from .models import MealRequest, MealResponse
from .services import generate_meal

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
            cuisine_type=request.cuisine_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))