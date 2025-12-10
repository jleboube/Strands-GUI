import json
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, async_session_maker
from app.core.security import decode_token
from app.models.user import User
from app.models.agent import Agent, AgentRun, RunStatus
from app.models.api_key import APIKey
from app.services.agent_service import AgentService
from app.services.strands_service import StrandsService

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)


manager = ConnectionManager()


async def get_user_from_token(token: str) -> User:
    """Validate token and get user"""
    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.id == int(user_id)))
        return result.scalar_one_or_none()


@router.websocket("/chat/{agent_id}")
async def websocket_chat(
    websocket: WebSocket,
    agent_id: int,
    token: str = Query(...),
):
    """WebSocket endpoint for real-time agent chat with streaming"""
    # Authenticate user
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(websocket, user.id)

    try:
        async with async_session_maker() as db:
            # Get agent
            agent_service = AgentService(db)
            agent = await agent_service.get_by_id(agent_id, user.id)

            if not agent:
                await websocket.send_json({
                    "type": "error",
                    "message": "Agent not found"
                })
                await websocket.close(code=4004)
                return

            # Get API credentials
            api_credentials = {}
            result = await db.execute(
                select(APIKey).where(
                    APIKey.user_id == user.id,
                    APIKey.provider == agent.model_provider
                )
            )
            api_key = result.scalar_one_or_none()
            if api_key:
                api_credentials = {
                    "api_key": api_key.api_key_encrypted,
                    "aws_access_key_id": api_key.aws_access_key_encrypted,
                    "aws_secret_access_key": api_key.aws_secret_key_encrypted,
                    "aws_region": api_key.aws_region,
                    "ollama_host": api_key.ollama_host,
                }

            # Get tools
            tools = [at.tool for at in agent.tools if at.enabled]

            # Send ready message
            await websocket.send_json({
                "type": "ready",
                "agent_id": agent_id,
                "agent_name": agent.name,
            })

            conversation_history = []
            strands_service = StrandsService()

            while True:
                # Receive message from client
                data = await websocket.receive_json()

                if data.get("type") == "message":
                    input_text = data.get("content", "")

                    if not input_text:
                        continue

                    # Create run record
                    run = await agent_service.create_run(
                        agent_id=agent.id,
                        input_text=input_text,
                        conversation_history=conversation_history,
                    )

                    # Update run status
                    run = await agent_service.update_run(
                        run,
                        status=RunStatus.RUNNING,
                        start_time=datetime.utcnow()
                    )

                    # Send thinking status
                    await websocket.send_json({
                        "type": "status",
                        "status": "thinking",
                        "run_id": run.id,
                    })

                    try:
                        # Stream response
                        full_response = ""
                        async for chunk in strands_service.stream_agent(
                            agent=agent,
                            tools=tools,
                            input_text=input_text,
                            conversation_history=conversation_history,
                            api_credentials=api_credentials,
                        ):
                            full_response += chunk
                            await websocket.send_json({
                                "type": "chunk",
                                "content": chunk,
                                "run_id": run.id,
                            })

                        # Update conversation history
                        conversation_history.append({"role": "user", "content": input_text})
                        conversation_history.append({"role": "assistant", "content": full_response})

                        # Update run as completed
                        run = await agent_service.update_run(
                            run,
                            status=RunStatus.COMPLETED,
                            output_text=full_response,
                            end_time=datetime.utcnow(),
                            conversation_history=conversation_history,
                        )

                        # Send complete message
                        await websocket.send_json({
                            "type": "complete",
                            "content": full_response,
                            "run_id": run.id,
                        })

                    except Exception as e:
                        # Update run as failed
                        run = await agent_service.update_run(
                            run,
                            status=RunStatus.FAILED,
                            error_message=str(e),
                            end_time=datetime.utcnow(),
                        )

                        await websocket.send_json({
                            "type": "error",
                            "message": str(e),
                            "run_id": run.id,
                        })

                elif data.get("type") == "clear_history":
                    conversation_history = []
                    await websocket.send_json({
                        "type": "history_cleared",
                    })

                elif data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(user.id)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Connection error: {str(e)}"
        })
        manager.disconnect(user.id)
