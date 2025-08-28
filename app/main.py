# app/main.py
from __future__ import annotations

import json
import os
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .api import router

app = FastAPI(title="QuantAlert API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api/v1")

if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root():
    """Serve the main web interface"""
    index_path = "app/static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({
        "message": "QuantAlert API",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws"
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "QuantAlert API is running",
        "websocket_connections": len(websocket_connections)
    }

# WebSocket Management
websocket_connections: Set[WebSocket] = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time price updates"""
    await websocket.accept()
    websocket_connections.add(websocket)
    print(f"📡 New WebSocket connection. Total: {len(websocket_connections)}")
    
    try:
        while True:
            try:
                message = await websocket.receive_text()
                if message == "ping":
                    await websocket.send_text("pong")
            except Exception:
                break
    except WebSocketDisconnect:
        print("📡 WebSocket disconnected normally")
    except Exception as e:
        print(f"📡 WebSocket error: {e}")
    finally:
        websocket_connections.discard(websocket)
        print(f"📡 WebSocket removed. Total: {len(websocket_connections)}")

async def broadcast_to_websockets(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    if not websocket_connections:
        return
    
    message_json = json.dumps(message)
    stale_connections = []
    
    for websocket in list(websocket_connections):
        try:
            await websocket.send_text(message_json)
        except Exception:
            stale_connections.append(websocket)
    
    # Remove stale connections
    for stale_ws in stale_connections:
        websocket_connections.discard(stale_ws)
    
    if stale_connections:
        print(f"📡 Removed {len(stale_connections)} stale connections. Active: {len(websocket_connections)}")

# Make broadcast function available
app.state.broadcast = broadcast_to_websockets

# ⭐ THIS IS THE MISSING ENDPOINT THAT FIXES THE 404 ERROR ⭐
@app.post("/_internal/broadcast")
async def internal_broadcast(payload: dict = Body(...)):
    """Internal endpoint for worker to broadcast price updates to WebSocket clients"""
    try:
        await broadcast_to_websockets(payload)
        print(f"📡 Broadcasted {payload.get('symbol', 'data')} to {len(websocket_connections)} clients")
        return {
            "ok": True, 
            "clients_notified": len(websocket_connections),
            "message": f"Broadcasted to {len(websocket_connections)} clients"
        }
    except Exception as e:
        print(f"❌ Broadcast error: {e}")
        return {"ok": False, "error": str(e)}

@app.get("/_internal/status")
async def internal_status():
    """Internal status endpoint for monitoring"""
    return {
        "websocket_connections": len(websocket_connections),
        "app_state": "running"
    }

# Application Lifecycle
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    print("🚀 QuantAlert API starting up...")
    print("📡 WebSocket endpoint: /ws")
    print("📊 API docs: /docs") 
    print("🔧 Health check: /health")
    print("🔄 Internal broadcast: /_internal/broadcast")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    print("🛑 QuantAlert API shutting down...")
    
    # Close all WebSocket connections gracefully
    for websocket in list(websocket_connections):
        try:
            await websocket.close(code=1001, reason="Server shutdown")
        except Exception:
            pass
    websocket_connections.clear()
    
    print("✅ All WebSocket connections closed")
