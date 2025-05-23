# app/services/meal_service.py
import os
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_meal(
    api_key: Optional[str] = None,
    meal_type: Optional[str] = None,
    include_ingredients: Optional[List[str]] = None,
    dietary_preferences: Optional[List[str]] = None,
    allergies: Optional[List[str]] = None,
    max_calories: Optional[int] = None,
    cuisine_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a meal with dietary preferences and restrictions.
    
    Args:
        api_key: OpenAI API key (optional if set in environment)
        meal_type: Type of meal (breakfast, lunch, dinner, snack, dessert)
        include_ingredients: List of ingredients to try to include (up to 5)
        dietary_preferences: List of dietary preferences (e.g., ["vegetarian", "keto", "pre-diabetic"])
        allergies: List of allergies to avoid
        max_calories: Maximum calories per serving
        cuisine_type: Preferred cuisine type
        
    Returns:
        Dict with meal name, ingredients, instructions, and dietary info
    """
    # Get API key
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OpenAI API key is required")
    
    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=key)
    except TypeError as e:
        if "proxies" in str(e):
            # Render sometimes passes proxy settings that OpenAI client doesn't accept
            # Initialize without any environment-based proxy settings
            import openai
            openai.api_key = key
            client = openai.OpenAI()
        else:
            raise e
    
    # Build dietary requirements text
    dietary_text = _build_dietary_requirements_text(
        meal_type, include_ingredients, dietary_preferences, allergies, max_calories, cuisine_type
    )
    
    # Create JSON-structured prompt
    prompt = f"""
    Generate a meal recipe with the following requirements:
    
    {dietary_text}
    
    You must respond with a valid JSON object in this exact format:
    {{
        "meal_name": "Name of the meal",
        "ingredients": ["ingredient 1 with quantity", "ingredient 2 with quantity"],
        "instructions": "Step-by-step cooking instructions in paragraph form",
        "estimated_calories": 400,
        "dietary_info": "Brief explanation of how this meal meets the dietary requirements"
    }}

    Make sure the JSON is valid and follows this structure exactly.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a nutritionist and chef who creates meals for specific dietary needs. Always respond with valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700,
            response_format={"type": "json_object"}
        )

        # Parse JSON response
        content = response.choices[0].message.content
        meal_data = json.loads(content)
        
        # Validate required fields and provide defaults
        return {
            "meal_name": meal_data.get("meal_name", "Untitled Meal"),
            "ingredients": meal_data.get("ingredients", []),
            "instructions": meal_data.get("instructions", "No instructions provided."),
            "estimated_calories": meal_data.get("estimated_calories"),
            "dietary_info": meal_data.get("dietary_info")
        }
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate meal: {str(e)}")


def _build_dietary_requirements_text(
    meal_type: Optional[str],
    include_ingredients: Optional[List[str]],
    dietary_preferences: Optional[List[str]],
    allergies: Optional[List[str]],
    max_calories: Optional[int],
    cuisine_type: Optional[str]
) -> str:
    """Build the dietary requirements section of the prompt."""
    requirements = []
    
    if meal_type:
        requirements.append(f"Meal type: {meal_type}")
    
    if include_ingredients and len(include_ingredients) > 0:
        ingredients_text = ", ".join(include_ingredients)
        requirements.append(f"REQUIRED INGREDIENTS: You MUST use the following ingredients in the recipe: {ingredients_text}")
    
    if dietary_preferences and len(dietary_preferences) > 0:
        pref_text = ", ".join(dietary_preferences)
        requirements.append(f"Dietary preferences: {pref_text}")
    
    if allergies and len(allergies) > 0:
        allergy_text = ", ".join(allergies)
        requirements.append(f"Avoid these allergens: {allergy_text}")
    
    if max_calories:
        requirements.append(f"Maximum {max_calories} calories per serving")
    
    if cuisine_type:
        requirements.append(f"Cuisine style: {cuisine_type}")
    
    if not requirements:
        return "No specific dietary restrictions."
    
    return "\n".join([f"- {req}" for req in requirements])