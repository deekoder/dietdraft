import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Optional

# Load environment variables
load_dotenv()

def generate_meal(api_key: Optional[str] = None) -> Dict:
    """
    Generate a simple meal with minimal structure.
    
    Args:
        api_key: OpenAI API key (optional if set in environment)
        
    Returns:
        Dict with meal name, ingredients list, and instructions
    """
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