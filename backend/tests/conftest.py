"""
Pytest configuration and fixtures for Strands GUI backend tests.
"""
import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment before importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DEBUG"] = "false"

from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.user import User
from app.models.agent import Agent, ModelProvider, AgentStatus
from app.models.tool import Tool, ToolType


# Create test database engine
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """Create and drop database tables for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for tests."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client with test database."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sync_client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Create sync test client for simple tests."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as tc:
        yield tc

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_token(test_user: User) -> str:
    """Create an auth token for the test user."""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
async def authenticated_client(
    client: AsyncClient,
    test_user_token: str
) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated async client."""
    client.headers["Authorization"] = f"Bearer {test_user_token}"
    yield client


@pytest.fixture
async def test_agent(db_session: AsyncSession, test_user: User) -> Agent:
    """Create a test agent."""
    agent = Agent(
        owner_id=test_user.id,
        name="Test Agent",
        description="A test agent for unit tests",
        system_prompt="You are a helpful test assistant.",
        model_provider=ModelProvider.BEDROCK,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        temperature=0.7,
        max_tokens=2048,
        streaming_enabled=True,
        mcp_enabled=False,
        status=AgentStatus.ACTIVE,
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


@pytest.fixture
async def test_tool(db_session: AsyncSession, test_user: User) -> Tool:
    """Create a test tool."""
    tool = Tool(
        owner_id=test_user.id,
        name="test_tool",
        display_name="Test Tool",
        description="A test tool for unit tests",
        tool_type=ToolType.CUSTOM,
        source_code='def test_tool(x): return x * 2',
        enabled=True,
        is_global=False,
    )
    db_session.add(tool)
    await db_session.commit()
    await db_session.refresh(tool)
    return tool


@pytest.fixture
async def builtin_tool(db_session: AsyncSession) -> Tool:
    """Create a built-in tool."""
    tool = Tool(
        owner_id=None,  # Built-in tools have no user
        name="calculator",
        display_name="Calculator",
        description="Perform mathematical calculations",
        tool_type=ToolType.BUILTIN,
        enabled=True,
        is_global=True,
    )
    db_session.add(tool)
    await db_session.commit()
    await db_session.refresh(tool)
    return tool


# Mock fixtures for Strands SDK
@pytest.fixture
def mock_strands_agent():
    """Create a mock Strands Agent."""
    mock_agent = MagicMock()
    mock_agent.return_value = "Mock response from agent"
    mock_agent.stream = MagicMock(return_value=iter(["chunk1", "chunk2"]))
    return mock_agent


@pytest.fixture
def mock_bedrock_model():
    """Create a mock Bedrock model."""
    mock_model = MagicMock()
    mock_model.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    return mock_model


@pytest.fixture
def mock_strands_service(mock_strands_agent, mock_bedrock_model):
    """Patch StrandsService for tests."""
    with patch("app.services.strands_service.StrandsService") as mock_service:
        instance = mock_service.return_value
        instance.create_strands_agent.return_value = mock_strands_agent
        instance._get_model_provider.return_value = mock_bedrock_model
        instance.run_agent = AsyncMock(return_value={
            "success": True,
            "output": "Mock agent response",
            "response_time_ms": 100,
            "tokens_used": 50,
        })
        instance.stream_agent = AsyncMock(return_value=iter(["chunk1", "chunk2"]))
        yield instance


# Helper fixtures for common test data
@pytest.fixture
def agent_create_data():
    """Sample data for creating an agent."""
    return {
        "name": "New Test Agent",
        "description": "A new agent created in tests",
        "system_prompt": "You are a helpful assistant.",
        "model_provider": "bedrock",
        "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
        "temperature": 0.5,
        "max_tokens": 4096,
        "streaming_enabled": True,
        "mcp_enabled": False,
        "tools": [],
    }


@pytest.fixture
def tool_create_data():
    """Sample data for creating a tool."""
    return {
        "name": "custom_tool",
        "display_name": "Custom Tool",
        "description": "A custom tool for testing",
        "tool_type": "custom",
        "source_code": """
from strands.tools import tool

@tool
def custom_tool(input: str) -> str:
    \"\"\"A custom tool that processes input.\"\"\"
    return f"Processed: {input}"
""",
    }


@pytest.fixture
def user_register_data():
    """Sample data for user registration."""
    return {
        "email": "newuser@example.com",
        "password": "securepassword123",
        "full_name": "New User",
    }
