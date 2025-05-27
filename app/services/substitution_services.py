import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def find_substitutions(
    original_ingredient: str,
    reason: str,
    recipe_context: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find ingredient substitutions using OpenAI.
    
    Args:
        original_ingredient: The ingredient to substitute
        reason: Why substitution is needed
        recipe_context: Optional context about recipe usage
        api_key: OpenAI API key
        
    Returns:
        Dict with substitution alternatives
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
            import openai
            openai.api_key = key
            client = openai.OpenAI()
        else:
            raise e
    
    # Build context information
    context_text = f"Recipe context: {recipe_context}" if recipe_context else ""
    
    # Create the prompt
    prompt = f"""
    Find ingredient substitutions for the following:
    
    Original ingredient: {original_ingredient}
    Reason for substitution: {reason}
    {context_text}
    
    Provide 3-5 alternative ingredients that would work as substitutions. 
    Focus on ingredients that address the substitution reason while maintaining 
    the dish's integrity.
    
    Respond with valid JSON in this format:
    {{
        "substitutions": [
            {{
                "ingredient": "coconut cream",
                "notes": "Use same amount. Provides richness but adds subtle coconut flavor."
            }},
            {{
                "ingredient": "cashew cream",
                "notes": "Blend 1 cup cashews with 1 cup water. Neutral flavor, very creamy."
            }}
        ]
    }}
    
    Make the notes practical and specific about usage.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a culinary expert who provides practical ingredient substitutions. Always respond with valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400,
            response_format={"type": "json_object"}
        )

        # Parse JSON response
        content = response.choices[0].message.content
        substitution_data = json.loads(content)
        
        # Return the structured response
        return {
            "original_ingredient": original_ingredient,
            "reason": reason,
            "substitutions": substitution_data.get("substitutions", [])
        }
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse substitution response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to find substitutions: {str(e)}")