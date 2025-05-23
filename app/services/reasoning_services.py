# app/services/reasoning_service.py
import os
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_meal_reasoning(
    api_key: Optional[str] = None,
    meal_name: str = "",
    ingredients: List[str] = [],
    instructions: Optional[str] = None,
    dietary_preferences: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate minimalistic reasoning about a meal.
    
    Args:
        api_key: OpenAI API key (optional if set in environment)
        meal_name: Name of the meal to analyze
        ingredients: List of ingredients in the meal
        instructions: Cooking instructions (optional)
        dietary_preferences: Dietary preferences to consider (optional)
        
    Returns:
        Dict with meal name and reasoning highlights
    """
    # Get API key
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OpenAI API key is required")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=key)
    
    # Format the ingredients for the prompt
    ingredients_text = "\n".join([f"- {ingredient}" for ingredient in ingredients])
    
    # Format dietary preferences if provided
    dietary_text = ""
    if dietary_preferences and len(dietary_preferences) > 0:
        dietary_text = f"Dietary preferences: {', '.join(dietary_preferences)}"
    
    # Create the prompt
    prompt = f"""
    Generate brief nutritional reasoning about this meal:
    
    Meal Name: {meal_name}
    
    Ingredients:
    {ingredients_text}
    
    {f"Instructions: {instructions}" if instructions else ""}
    
    {dietary_text}
    
    Provide concise reasoning (1-2 sentences each) in this exact JSON format:
    {{
        "key_ingredient_choices": "Brief explanation of why key ingredients were selected and their nutritional significance",
        "nutritional_benefits": "Key nutritional benefits of this meal, including macronutrient balance",
        "dietary_alignment": "How this meal aligns with the specified dietary preferences"
    }}
    
    Keep explanations concise, evidence-based, and focused on nutritional value.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using the smaller model for efficiency
            messages=[
                {
                    "role": "system", 
                    "content": "You are a nutritionist who provides concise, evidence-based explanations about meals."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,  # Limiting tokens for brevity
            response_format={"type": "json_object"}
        )

        # Parse JSON response
        content = response.choices[0].message.content
        reasoning_data = json.loads(content)
        
        # Return the structured response
        return {
            "meal_name": meal_name,
            "reasoning": {
                "key_ingredient_choices": reasoning_data.get("key_ingredient_choices", ""),
                "nutritional_benefits": reasoning_data.get("nutritional_benefits", ""),
                "dietary_alignment": reasoning_data.get("dietary_alignment", "")
            }
        }
        
    except Exception as e:
        raise Exception(f"Failed to generate reasoning: {str(e)}")