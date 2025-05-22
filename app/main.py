# app/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from openai import OpenAI
from dotenv import load_dotenv
import pathlib

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


# Find the directory where this file is located
CURRENT_DIR = pathlib.Path(__file__).parent
STATIC_DIR = CURRENT_DIR / "static"

# Assuming static files are in a directory called 'static' at the project root
# Mount static files for web client
print("---->",STATIC_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Simple request and response models
class MealRequest(BaseModel):
    api_key: Optional[str] = None

class MealResponse(BaseModel):
    meal_name: str
    ingredients: List[str]
    instructions: str

# Meal generation function
def generate_meal(api_key: Optional[str] = None):
    """Generate a simple meal with minimal structure."""
    # Get API key
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OpenAI API key is required")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=key)
    
    # Simple prompt to generate a meal
    prompt = """
    Generate a simple meal recipe with:
    1. A name for the meal
    2. A list of ingredients (just 5-10 items)
    3. Brief cooking instructions (1-2 paragraphs)
    
    Keep it simple and straightforward.
    """
    
    try:
        # Using gpt-3.5-turbo - the most cost-effective model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates meal recipes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Get the response text
        content = response.choices[0].message.content
        
        # Parse the content into sections using basic string operations
        lines = content.strip().split('\n')
        
        # Extract meal name (first non-empty line)
        meal_name = next((line for line in lines if line.strip()), "Untitled Meal")
        
        # Find ingredient section
        ingredients_start = None
        instructions_start = None
        
        for i, line in enumerate(lines):
            lower_line = line.lower()
            if "ingredient" in lower_line and ingredients_start is None:
                ingredients_start = i + 1
            elif "instruction" in lower_line or "direction" in lower_line:
                instructions_start = i + 1
                break
        
        # Default values in case parsing fails
        ingredients = []
        instructions = "No instructions provided."
        
        # Extract ingredients if section was found
        if ingredients_start is not None and instructions_start is not None:
            ingredients_section = lines[ingredients_start:instructions_start-1]
            ingredients = [line.strip().lstrip('- ') for line in ingredients_section if line.strip()]
        
        # Extract instructions if section was found
        if instructions_start is not None:
            instructions_section = lines[instructions_start:]
            instructions = "\n".join(instructions_section).strip()
        
        return {
            "meal_name": meal_name,
            "ingredients": ingredients,
            "instructions": instructions
        }
    except Exception as e:
        raise Exception(f"Failed to generate meal: {str(e)}")

# API endpoints
@app.get("/")
async def root():
    """Root endpoint redirecting to web client."""
    return {"message": "Visit /static/index.html for web client"}

@app.post("/generate-meal", response_model=MealResponse)
async def api_generate_meal(request: MealRequest):
    """Generate a single meal."""
    try:
        result = generate_meal(request.api_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))