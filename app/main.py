# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import custom documentation service
from .services.custom_docs_service import add_custom_docs_route

# Import routes
from .routes.meal_routes import router as meal_router
from .routes.reasoning_routes import router as reasoning_router
from .routes.voice_routes import router as voice_router   
from .routes.substitution_routes import router as substitution_router
from .routes.diet_coach_routes import router as diet_coach_router

# Create FastAPI app
app = FastAPI(
    title="DietDraft API",
    description="AI-powered meal planning and nutritional reasoning API",
    version="0.2.0",
    docs_url=None,  # Disable default docs to use our custom docs
    openapi_tags=[
        {
            "name": "Meals",
            "description": "Endpoints for generating meal recipes based on preferences"
        },
        {
            "name": "Nutrition",
            "description": "Endpoints for nutritional analysis and reasoning"
        },
        {  # Add this section
            "name": "Voice",
            "description": "Endpoints for processing voice input"
        },
        {
            "name": "Tools",  # New category
            "description": "Individual tools for ingredient substitutions and meal planning"
        },
        {
            "name": "Diet Coach",  # New category
            "description": "Your AI diet coach for personalized nutrition guidance"
        }
    ]
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dietdraft-web.onrender.com",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add custom documentation
add_custom_docs_route(app)

# Include routers
app.include_router(meal_router, prefix="", tags=["Meals"])
app.include_router(reasoning_router, prefix="", tags=["Nutrition"])
app.include_router(voice_router, prefix="", tags=["Voice"])
app.include_router(substitution_router, prefix="", tags=["Tools"])
app.include_router(diet_coach_router, prefix="", tags=["Diet Coach"]) 



# Root endpoint redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to docs"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")