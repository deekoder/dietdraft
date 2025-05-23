# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import custom documentation service (updated import path)
from .services.custom_docs_service import add_custom_docs_route

# Import routes
from .routes.meal_routes import router as meal_router
from .routes.reasoning_routes import router as reasoning_router

# Create FastAPI app
app = FastAPI(
    title="DietDraft API",
    description="AI-powered meal planning and nutritional reasoning API",
    version="0.1.0",
    docs_url=None,  # Disable default docs to use our custom docs
    openapi_tags=[
        {
            "name": "Meals",
            "description": "Endpoints for generating meal recipes based on preferences"
        },
        {
            "name": "Nutrition",
            "description": "Endpoints for nutritional analysis and reasoning"
        }
    ]
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom documentation
add_custom_docs_route(app)

# Include routers
app.include_router(meal_router, prefix="", tags=["Meals"])
app.include_router(reasoning_router, prefix="", tags=["Nutrition"])

# Root endpoint redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to docs"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")