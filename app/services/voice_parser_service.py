# app/services/voice_parser_service.py
import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def parse_voice_to_json(
    voice_text: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use LLM to parse voice text into structured meal request JSON.
    
    Args:
        voice_text: Raw text transcribed from voice input
        api_key: OpenAI API key (optional if set in environment)
        
    Returns:
        Dict with structured meal request parameters
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
    
    # Create prompt for the LLM
    prompt = f"""
    Parse the following voice input into a JSON structure for a meal recipe API.
    
    Voice Input: "{voice_text}"
    
    Extract the following information (if present):
    - meal_type: (breakfast, lunch, dinner, snack, or dessert)
    - include_ingredients: (list of ingredients mentioned)
    - dietary_preferences: (like vegetarian, vegan, gluten-free, etc.)
    - allergies: (any allergies or ingredients to avoid)
    - max_calories: (calorie limit if mentioned)
    - cuisine_type: (cuisine style like Italian, Mexican, etc.)
    
    Return ONLY a valid JSON object with these fields. If a field is not mentioned, use null or an empty array as appropriate.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Could use a smaller/cheaper model for this task
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that parses voice commands into structured JSON for a recipe API."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more deterministic parsing
            max_tokens=300,
            response_format={"type": "json_object"}
        )

        # Parse JSON response
        content = response.choices[0].message.content
        parsed_data = json.loads(content)
        
        # Add a human-readable summary
        parsed_data["parsed_text"] = generate_human_readable_summary(parsed_data)
        
        return parsed_data
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse LLM response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to parse voice input: {str(e)}")

def generate_human_readable_summary(parsed_data: Dict[str, Any]) -> str:
    """Generate a human-readable summary of the parsed data."""
    summary = []
    
    if parsed_data.get("meal_type"):
        summary.append(f"Meal type: {parsed_data['meal_type'].capitalize()}")
    
    if parsed_data.get("include_ingredients") and len(parsed_data["include_ingredients"]) > 0:
        summary.append(f"Ingredients: {', '.join(parsed_data['include_ingredients'])}")
    
    if parsed_data.get("dietary_preferences") and len(parsed_data["dietary_preferences"]) > 0:
        summary.append(f"Dietary preferences: {', '.join(parsed_data['dietary_preferences'])}")
    
    if parsed_data.get("allergies") and len(parsed_data["allergies"]) > 0:
        summary.append(f"Allergies: {', '.join(parsed_data['allergies'])}")
    
    if parsed_data.get("cuisine_type"):
        summary.append(f"Cuisine: {parsed_data['cuisine_type'].capitalize()}")
    
    if parsed_data.get("max_calories"):
        summary.append(f"Maximum calories: {parsed_data['max_calories']}")
    
    if not summary:
        return "I couldn't understand specific meal requirements from your input."
    
    return "\n".join(summary)