# app/routes/substitution_routes.py
from fastapi import APIRouter, HTTPException
from app.models.substitution_models import SubstitutionRequest, SubstitutionResponse, SubstitutionOption
from app.services.substitution_services import find_substitutions

router = APIRouter()

@router.post("/find-substitutions", response_model=SubstitutionResponse)
async def api_find_substitutions(request: SubstitutionRequest):
    """
    Find ingredient substitutions for dietary needs or preferences.
    
    This endpoint suggests alternative ingredients when you need to replace 
    an ingredient due to allergies, dietary restrictions, or availability.
    
    Example request:
    ```json
    {
      "original_ingredient": "heavy cream",
      "reason": "dairy-free",
      "recipe_context": "creamy pasta sauce"
    }
    ```
    """
    try:
        result = find_substitutions(
            original_ingredient=request.original_ingredient,
            reason=request.reason,
            recipe_context=request.recipe_context,
            api_key=request.api_key
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))