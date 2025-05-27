# app/services/diet_coach_service.py
import os
import json
import uuid
import re
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Import tool services
from app.services.meal_service import generate_meal
from app.services.substitution_services import find_substitutions
from app.services.reasoning_services import generate_meal_reasoning

load_dotenv()

# Simple in-memory conversation storage (will replace with Supabase later)
conversations = {}

def analyze_user_intent(message: str, api_key: str) -> Dict[str, Any]:
    """
    Analyze user message to determine intent and extract key information.
    
    Args:
        message: User's message
        api_key: OpenAI API key
        
    Returns:
        Dict with intent analysis and extracted information
    """
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    Analyze this user message and extract information:
    
    Message: "{message}"
    
    Extract and determine:
    1. Primary intent (what do they want?)
    2. Any specific ingredients mentioned
    3. Any dietary preferences mentioned
    4. Any substitution needs
    5. What tools should be used to help them
    
    Available tools:
    - generate_meal: Create a new recipe
    - find_substitutions: Find ingredient alternatives  
    - meal_reasoning: Analyze nutritional aspects
    
    Respond with JSON:
    {{
        "intent": "generate_recipe" | "find_substitutions" | "analyze_nutrition" | "general_question",
        "tools_needed": ["generate_meal"],
        "extracted_info": {{
            "ingredients": ["chicken", "broccoli"],
            "dietary_preferences": ["high-protein", "low-carb"],
            "substitution_requests": [
                {{"ingredient": "butter", "reason": "dairy-free"}}
            ],
            "meal_type": "dinner",
            "allergies": ["nuts"]
        }},
        "confidence": 0.8
    }}
    
    Only include information that is explicitly mentioned in the message.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an intent analysis system for a diet coach. Always respond with valid JSON. Only extract information explicitly mentioned by the user."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=400,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        # Fallback analysis
        return {
            "intent": "generate_recipe" if any(word in message.lower() for word in ["make", "recipe", "cook", "meal"]) else "general_question",
            "tools_needed": ["generate_meal"],
            "extracted_info": {},
            "confidence": 0.3
        }

def execute_tools(intent_analysis: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """
    Execute the appropriate tools based on intent analysis.
    
    Args:
        intent_analysis: Results from analyze_user_intent
        api_key: OpenAI API key
        
    Returns:
        Dict with tool results
    """
    tools_used = []
    tool_results = {}
    extracted_info = intent_analysis.get("extracted_info", {})
    
    # Handle substitution requests
    if "find_substitutions" in intent_analysis.get("tools_needed", []):
        substitution_requests = extracted_info.get("substitution_requests", [])
        if substitution_requests:
            substitution_results = []
            for sub_req in substitution_requests:
                try:
                    result = find_substitutions(
                        original_ingredient=sub_req.get("ingredient", ""),
                        reason=sub_req.get("reason", "dietary preference"),
                        api_key=api_key
                    )
                    substitution_results.append(result)
                    tools_used.append("find_substitutions")
                except Exception as e:
                    tool_results[f"substitution_error"] = str(e)
            
            if substitution_results:
                tool_results["substitutions"] = substitution_results
    
    # Handle meal generation
    if "generate_meal" in intent_analysis.get("tools_needed", []):
        try:
            # Build meal request from extracted info
            meal_params = {}
            
            if extracted_info.get("ingredients"):
                meal_params["include_ingredients"] = extracted_info["ingredients"]
            
            if extracted_info.get("dietary_preferences"):
                meal_params["dietary_preferences"] = extracted_info["dietary_preferences"]
            
            if extracted_info.get("meal_type"):
                meal_params["meal_type"] = extracted_info["meal_type"]
            
            if extracted_info.get("allergies"):
                meal_params["allergies"] = extracted_info["allergies"]
            
            # Generate meal with extracted parameters
            meal_result = generate_meal(api_key=api_key, **meal_params)
            tool_results["meal"] = meal_result
            tools_used.append("generate_meal")
            
        except Exception as e:
            tool_results["meal_error"] = str(e)
    
    # Handle nutritional reasoning (if meal was generated)
    if "meal_reasoning" in intent_analysis.get("tools_needed", []) and "meal" in tool_results:
        try:
            meal = tool_results["meal"]
            reasoning_result = generate_meal_reasoning(
                api_key=api_key,
                meal_name=meal.get("meal_name", "Generated Meal"),
                ingredients=meal.get("ingredients", []),
                dietary_preferences=extracted_info.get("dietary_preferences", [])
            )
            tool_results["reasoning"] = reasoning_result
            tools_used.append("meal_reasoning")
            
        except Exception as e:
            tool_results["reasoning_error"] = str(e)
    
    return {
        "tools_used": tools_used,
        "results": tool_results
    }

def generate_coach_response(
    message: str,
    conversation_history: List[Dict],
    intent_analysis: Dict[str, Any],
    tool_execution: Dict[str, Any],
    api_key: str
) -> str:
    """
    Generate a personalized coaching response based on context and tool results.
    """
    client = OpenAI(api_key=api_key)
    
    # Build context from conversation history
    history_context = ""
    if len(conversation_history) > 2:
        recent_messages = conversation_history[-4:]  # Last 2 exchanges
        history_context = "Previous conversation context:\n"
        for msg in recent_messages[:-1]:  # Exclude current message
            role = "User" if msg["role"] == "user" else "Diet Coach"
            history_context += f"{role}: {msg['content'][:100]}...\n"
    
    # Build tool results context
    tool_results = tool_execution.get("results", {})
    tool_context = ""
    
    if "meal" in tool_results:
        meal = tool_results["meal"]
        tool_context += f"Generated meal: {meal.get('meal_name', 'Unknown')}\n"
        tool_context += f"Ingredients: {', '.join(meal.get('ingredients', []))}\n"
        if meal.get("dietary_info"):
            tool_context += f"Dietary info: {meal.get('dietary_info')}\n"
    
    if "substitutions" in tool_results:
        subs = tool_results["substitutions"]
        tool_context += "Found substitutions:\n"
        for sub in subs:
            tool_context += f"- {sub.get('original_ingredient')} alternatives: "
            alt_names = [alt.get('ingredient', '') for alt in sub.get('substitutions', [])]
            tool_context += ", ".join(alt_names[:3]) + "\n"
    
    if "reasoning" in tool_results:
        reasoning = tool_results["reasoning"].get("reasoning", {})
        tool_context += f"Nutritional benefits: {reasoning.get('nutritional_benefits', '')}\n"
    
    # Handle errors gracefully
    error_context = ""
    for key, value in tool_results.items():
        if "error" in key:
            error_context += f"Note: Had trouble with {key.replace('_error', '')}: {value}\n"
    
    prompt = f"""
    You are a friendly, knowledgeable diet coach. Respond to the user's message in a 
    supportive and informative coaching style.
    
    {history_context}
    
    User's current message: "{message}"
    
    {tool_context}
    
    {error_context}
    
    As a diet coach, provide a helpful response that:
    1. Acknowledges what the user asked for
    2. Presents any generated recipes or substitutions clearly
    3. Offers nutritional insights when relevant
    4. Asks follow-up questions if more information would be helpful
    5. Uses encouraging, professional coaching language
    
    Keep the response conversational but informative. If you generated a meal, 
    present it in an organized way. If you found substitutions, explain why 
    they work well.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional diet coach who provides helpful, encouraging guidance about nutrition and meal planning. Be friendly, knowledgeable, and supportive."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return "I'm here to help you with your nutrition goals! Could you tell me a bit more about what you're looking for today?"

def process_diet_coach_request(
    message: str,
    conversation_id: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main diet coach processing function with tool selection and execution.
    
    Args:
        message: User's message
        conversation_id: Optional conversation ID for context
        api_key: OpenAI API key
        
    Returns:
        Dict with coach response and tool results
    """
    # Get API key
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OpenAI API key is required")
    
    # Generate conversation ID if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    # Get or create conversation history
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    conversation_history = conversations[conversation_id]
    
    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": message,
        "timestamp": "now"
    })
    
    # Step 1: Analyze user intent and extract information
    intent_analysis = analyze_user_intent(message, key)
    
    # Step 2: Execute appropriate tools
    tool_execution = execute_tools(intent_analysis, key)
    
    # Step 3: Generate coaching response
    coach_response = generate_coach_response(
        message=message,
        conversation_history=conversation_history,
        intent_analysis=intent_analysis,
        tool_execution=tool_execution,
        api_key=key
    )
    
    # Add coach response to history
    conversation_history.append({
        "role": "assistant",
        "content": coach_response,
        "timestamp": "now"
    })
    
    # Update conversation storage
    conversations[conversation_id] = conversation_history
    
    return {
        "response": coach_response,
        "action_taken": intent_analysis.get("intent"),
        "tools_used": tool_execution.get("tools_used", []),
        "conversation_id": conversation_id,
        "data": tool_execution.get("results", {})
    }