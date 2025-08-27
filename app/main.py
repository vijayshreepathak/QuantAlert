from fastapi import FastAPI
from fastapi import WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .api import router
import os

# Create database tables
# Base.metadata.create_all(bind=engine) # This line was removed as per the new_code, as the engine and Base are no longer imported.

app = FastAPI(title="QuantAlert API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Serve static files
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root():
    """Serve the main web interface"""
    return FileResponse("app/static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "QuantAlert API is running"}

# WebSocket connections storage
websocket_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except:
        pass
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

# Function to broadcast to all WebSocket connections
async def broadcast_to_websockets(message):
    """Broadcast message to all connected WebSocket clients"""
    import json
    message_json = json.dumps(message)
    
    for websocket in websocket_connections[:]:  # Copy list to avoid modification during iteration
        try:
            await websocket.send_text(message_json)
        except:
            # Remove disconnected websockets
            if websocket in websocket_connections:
                websocket_connections.remove(websocket)

# Make broadcast function available to other modules
app.state.broadcast = broadcast_to_websockets
