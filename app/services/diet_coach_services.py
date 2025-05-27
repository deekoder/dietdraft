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

# Simple in-memory conversation storage with better session management
conversations = {}

def process_diet_coach_request(
    message: str,
    conversation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main diet coach processing function with improved session management.
    
    Args:
        message: User's message
        conversation_id: Optional conversation ID for context
        user_id: Optional user ID for session management
        api_key: OpenAI API key
        
    Returns:
        Dict with coach response and tool results
    """
    # Get API key
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OpenAI API key is required")
    
    # Generate user_id if not provided (anonymous user)
    if not user_id:
        user_id = str(uuid.uuid4())
    
    # Generate conversation ID if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    # Get or create conversation history in memory
    # Using user_id as part of the key for better session management
    session_key = f"{user_id}:{conversation_id}"
    
    if session_key not in conversations:
        conversations[session_key] = []
        print(f"Created new conversation: {session_key}")
    else:
        print(f"Continuing conversation: {session_key} (has {len(conversations[session_key])} messages)")
    
    conversation_history = conversations[session_key]
    
    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": message,
        "timestamp": "now"
    })
    
    # Step 1: Analyze user intent with conversation context
    intent_analysis = analyze_user_intent_with_context(message, conversation_history, key)
    
    # Step 2: Execute appropriate tools
    tool_execution = execute_tools(intent_analysis, key)
    
    # Step 3: Generate coaching response
    coach_response = generate_coach_response_with_context(
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
    conversations[session_key] = conversation_history
    
    print(f"Updated conversation {session_key}: now has {len(conversation_history)} messages")
    
    return {
        "response": coach_response,
        "action_taken": intent_analysis.get("intent"),
        "tools_used": tool_execution.get("tools_used", []),
        "conversation_id": conversation_id,
        "user_id": user_id,
        "data": tool_execution.get("results", {})
    }

def analyze_user_intent_with_context(
    message: str, 
    conversation_history: List[Dict], 
    api_key: str
) -> Dict[str, Any]:
    """
    Analyze user message with conversation context (simplified for in-memory version).
    """
    client = OpenAI(api_key=api_key)
    
    # Build context from conversation history
    context_text = ""
    if len(conversation_history) > 2:  # More than just current message
        context_text = "Recent conversation:\n"
        for msg in conversation_history[-6:-1]:  # Last few messages, excluding current
            role = "User" if msg["role"] == "user" else "Diet Coach"
            context_text += f"{role}: {msg['content'][:100]}...\n"
    
    prompt = f"""
    Analyze this user message in context:
    
    Current message: "{message}"
    
    {context_text}
    
    Based on the conversation context, determine:
    1. What the user is asking for
    2. What tools should be used
    3. What information can be extracted
    4. How this relates to previous conversation
    
    Available tools:
    - generate_meal: Create a new recipe
    - find_substitutions: Find ingredient alternatives  
    - meal_reasoning: Analyze nutritional aspects
    
    Respond with JSON:
    {{
        "intent": "generate_recipe" | "find_substitutions" | "analyze_nutrition" | "general_question" | "follow_up",
        "tools_needed": ["generate_meal"],
        "extracted_info": {{
            "ingredients": ["chicken", "broccoli"],
            "dietary_preferences": ["high-protein", "low-carb"],
            "substitution_requests": [
                {{"ingredient": "butter", "reason": "dairy-free"}}
            ],
            "meal_type": "dinner",
            "allergies": ["nuts"],
            "references_previous": true
        }},
        "confidence": 0.8,
        "context_understanding": "User is asking for modifications to previously generated meal"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an intent analysis system for a diet coach. Use conversation context to understand requests. Always respond with valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=400,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        # Enhanced fallback with conversation awareness
        has_previous_context = len(conversation_history) > 2
        
        return {
            "intent": "follow_up" if has_previous_context else "generate_recipe",
            "tools_needed": ["generate_meal"],
            "extracted_info": {
                "references_previous": has_previous_context
            },
            "confidence": 0.3,
            "context_understanding": "Fallback analysis due to parsing error"
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

def generate_coach_response_with_context(
    message: str,
    conversation_history: List[Dict],
    intent_analysis: Dict[str, Any],
    tool_execution: Dict[str, Any],
    api_key: str
) -> str:
    """
    Generate a personalized coaching response with conversation context.
    """
    client = OpenAI(api_key=api_key)
    
    # Build rich context from conversation history
    history_context = ""
    if len(conversation_history) > 2:
        recent_messages = conversation_history[-6:-1]  # Last few exchanges, excluding current
        history_context = "Conversation context:\n"
        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Diet Coach"
            history_context += f"{role}: {msg['content'][:150]}...\n"
    
    # Build tool results context with better formatting
    tool_results = tool_execution.get("results", {})
    tool_context = ""
    
    if "meal" in tool_results:
        meal = tool_results["meal"]
        tool_context += f"Generated meal: {meal.get('meal_name', 'Unknown')}\n"
        if meal.get("ingredients"):
            tool_context += f"Key ingredients: {', '.join(meal.get('ingredients', [])[:3])}...\n"
        if meal.get("dietary_info"):
            tool_context += f"Dietary benefits: {meal.get('dietary_info')}\n"
    
    if "substitutions" in tool_results:
        subs = tool_results["substitutions"]
        tool_context += f"Found {len(subs)} substitution group(s):\n"
        for sub in subs[:2]:  # Show first 2
            alternatives = [alt.get('ingredient', '') for alt in sub.get('substitutions', [])[:2]]
            tool_context += f"- {sub.get('original_ingredient')} → {', '.join(alternatives)}\n"
    
    if "reasoning" in tool_results:
        reasoning = tool_results["reasoning"].get("reasoning", {})
        if reasoning.get("nutritional_benefits"):
            tool_context += f"Nutritional insight: {reasoning.get('nutritional_benefits')[:100]}...\n"
    
    # Handle context awareness
    context_awareness = intent_analysis.get("context_understanding", "")
    references_previous = intent_analysis.get("extracted_info", {}).get("references_previous", False)
    
    prompt = f"""
    You are a knowledgeable, friendly diet coach having an ongoing conversation with a user.
    
    {history_context}
    
    User's current message: "{message}"
    
    Context analysis: {context_awareness}
    References previous conversation: {references_previous}
    
    {tool_context}
    
    As their diet coach, provide a response that:
    1. Acknowledges the conversation context when relevant
    2. Presents any generated content (recipes, substitutions) clearly
    3. Relates back to previous conversation when appropriate
    4. Offers follow-up questions or suggestions
    5. Uses encouraging, professional coaching language
    6. Shows understanding of their ongoing needs
    
    Keep responses conversational, helpful, and personalized. If you used tools,
    integrate the results naturally into your coaching advice.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced diet coach who maintains context across conversations and provides personalized guidance. Be warm, knowledgeable, and helpful."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return "I'm here to help you with your nutrition goals! I'm having a technical moment - could you tell me again what you'd like to work on?"