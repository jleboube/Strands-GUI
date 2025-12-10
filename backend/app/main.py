from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import structlog

from app.core.config import settings
from app.core.database import init_db, async_session_maker
from app.api import api_router
from app.services.tool_service import ToolService
from app.services.agent_service import AgentService

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Strands Agents GUI", version=settings.APP_VERSION)

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Seed built-in tools and templates
    async with async_session_maker() as db:
        tool_service = ToolService(db)
        await tool_service.seed_builtin_tools()
        logger.info("Built-in tools seeded")

        agent_service = AgentService(db)
        await agent_service.seed_template_agents()
        logger.info("Template agents seeded")

    yield

    # Shutdown
    logger.info("Shutting down Strands Agents GUI")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Web-based GUI for Strands Agents SDK",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }


@app.get("/api/models")
async def list_models():
    """List available model providers and their models"""
    return {
        "providers": [
            {
                "id": "bedrock",
                "name": "Amazon Bedrock",
                "models": [
                    {"id": "anthropic.claude-3-5-sonnet-20241022-v2:0", "name": "Claude 3.5 Sonnet v2"},
                    {"id": "anthropic.claude-3-sonnet-20240229-v1:0", "name": "Claude 3 Sonnet"},
                    {"id": "anthropic.claude-3-haiku-20240307-v1:0", "name": "Claude 3 Haiku"},
                    {"id": "anthropic.claude-3-opus-20240229-v1:0", "name": "Claude 3 Opus"},
                    {"id": "amazon.titan-text-express-v1", "name": "Amazon Titan Text Express"},
                    {"id": "meta.llama3-70b-instruct-v1:0", "name": "Llama 3 70B"},
                    {"id": "mistral.mistral-large-2402-v1:0", "name": "Mistral Large"},
                ],
            },
            {
                "id": "gemini",
                "name": "Google Gemini",
                "models": [
                    {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
                    {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
                    {"id": "gemini-pro", "name": "Gemini Pro"},
                ],
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "models": [
                    {"id": "gpt-4o", "name": "GPT-4o"},
                    {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
                    {"id": "gpt-4", "name": "GPT-4"},
                    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
                ],
            },
            {
                "id": "anthropic",
                "name": "Anthropic",
                "models": [
                    {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
                    {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
                    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"},
                ],
            },
            {
                "id": "ollama",
                "name": "Ollama (Local)",
                "models": [
                    {"id": "llama3.2", "name": "Llama 3.2"},
                    {"id": "llama3.1", "name": "Llama 3.1"},
                    {"id": "mistral", "name": "Mistral"},
                    {"id": "codellama", "name": "Code Llama"},
                    {"id": "phi3", "name": "Phi-3"},
                ],
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
