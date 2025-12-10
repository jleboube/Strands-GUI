from fastapi import APIRouter

from app.api.routes import auth, agents, tools, api_keys, websocket

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
