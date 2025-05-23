# app/services/custom_docs_service.py
from fastapi import FastAPI
from starlette.responses import HTMLResponse

def add_custom_docs_route(app: FastAPI):
    """
    Add custom documentation route with minimal inline styling.
    
    Args:
        app: FastAPI application instance to add the route to
    """
    
    @app.get("/docs", include_in_schema=False)
    async def custom_docs():
        """Custom documentation with minimal inline styling"""
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
            <title>DietDraft API - Documentation</title>
            <style>
                /* Base styles */
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    color: #333;
                }
                
                /* Header styling */
                .topbar { 
                    background-color: #5469d4 !important; 
                }
                
                /* API operation styling */
                .opblock { 
                    margin: 0 0 15px 0 !important; 
                    border-radius: 6px !important; 
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important; 
                    border: 1px solid #e4e4e7 !important;
                }
                
                /* HTTP method colors */
                .opblock-get .opblock-summary-method { 
                    background-color: #3b82f6 !important; 
                }
                .opblock-post .opblock-summary-method { 
                    background-color: #10b981 !important; 
                }
                .opblock-put .opblock-summary-method { 
                    background-color: #f59e0b !important; 
                }
                .opblock-delete .opblock-summary-method { 
                    background-color: #ef4444 !important; 
                }
                
                /* Buttons */
                .btn.execute { 
                    background-color: #5469d4 !important; 
                    border-color: #5469d4 !important; 
                }
                
                /* Models section */
                .models h4 span {
                    color: #5469d4 !important;
                }
                
                /* Parameter styling */
                table.parameters td, table.parameters th {
                    padding: 10px !important;
                }
                
                .parameter__name {
                    font-weight: 600 !important;
                    font-family: monospace !important;
                }
                
                /* Tags */
                .opblock-tag {
                    font-size: 18px !important;
                    padding: 10px 0 !important;
                    margin: 15px 0 5px 0 !important;
                }
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
            <script>
                const ui = SwaggerUIBundle({
                    url: '/openapi.json',
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout",
                    deepLinking: true,
                    displayRequestDuration: true,
                    docExpansion: 'list',
                    filter: true
                });
            </script>
        </body>
        </html>
        """)