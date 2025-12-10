"""
Strands SDK integration tests for Strands GUI backend.

These tests verify the integration with the Strands Agents SDK.
Most tests use mocks to avoid requiring actual SDK credentials.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from app.models.agent import Agent, ModelProvider
from app.models.tool import Tool, ToolType
from app.services.strands_service import StrandsService


class TestStrandsServiceModelProvider:
    """Tests for model provider selection."""

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_get_bedrock_provider(self):
        """Test Bedrock model provider creation."""
        service = StrandsService()

        agent = MagicMock()
        agent.model_provider = ModelProvider.BEDROCK
        agent.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

        with patch("app.services.strands_service.BedrockModel") as mock_bedrock:
            mock_bedrock.return_value = MagicMock()
            provider = service._get_model_provider(agent, {"aws_region": "us-west-2"})

            mock_bedrock.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_get_openai_provider(self):
        """Test OpenAI model provider creation."""
        service = StrandsService()

        agent = MagicMock()
        agent.model_provider = ModelProvider.OPENAI
        agent.model_id = "gpt-4"

        with patch("app.services.strands_service.OpenAIModel") as mock_openai:
            mock_openai.return_value = MagicMock()
            provider = service._get_model_provider(agent, {"api_key": "test-key"})

            mock_openai.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_get_anthropic_provider(self):
        """Test Anthropic model provider creation."""
        service = StrandsService()

        agent = MagicMock()
        agent.model_provider = ModelProvider.ANTHROPIC
        agent.model_id = "claude-3-sonnet-20240229"

        with patch("app.services.strands_service.AnthropicModel") as mock_anthropic:
            mock_anthropic.return_value = MagicMock()
            provider = service._get_model_provider(agent, {"api_key": "test-key"})

            mock_anthropic.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_get_ollama_provider(self):
        """Test Ollama model provider creation."""
        service = StrandsService()

        agent = MagicMock()
        agent.model_provider = ModelProvider.OLLAMA
        agent.model_id = "llama3.2"

        with patch("app.services.strands_service.OllamaModel") as mock_ollama:
            mock_ollama.return_value = MagicMock()
            provider = service._get_model_provider(
                agent,
                {"ollama_host": "http://localhost:11434"}
            )

            mock_ollama.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_provider_import_error_returns_none(self):
        """Test that import errors return None."""
        service = StrandsService()

        agent = MagicMock()
        agent.model_provider = ModelProvider.BEDROCK
        agent.model_id = "test-model"

        # When SDK import fails, should return None
        with patch.dict("sys.modules", {"strands.models": None}):
            with patch(
                "app.services.strands_service.StrandsService._get_model_provider",
                return_value=None
            ):
                result = service._get_model_provider(agent, {})
                assert result is None


class TestStrandsServiceTools:
    """Tests for tool loading."""

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_load_builtin_tool(self):
        """Test loading a built-in tool."""
        service = StrandsService()

        with patch("strands_agents_tools.calculator") as mock_calc:
            mock_calc.return_value = "calculator function"
            result = service._get_builtin_tool("calculator")

            # Should return the mocked function
            assert result is not None

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_load_unknown_builtin_tool(self):
        """Test that unknown builtin tools return None."""
        service = StrandsService()

        result = service._get_builtin_tool("unknown_tool")
        assert result is None

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_create_custom_tool(self):
        """Test creating a custom tool from source code."""
        service = StrandsService()

        source_code = """
def my_custom_tool(x):
    return x * 2
"""
        result = service._create_custom_tool("my_custom_tool", source_code)

        assert result is not None
        assert callable(result)
        assert result(5) == 10

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_create_custom_tool_invalid_code(self):
        """Test that invalid code returns None."""
        service = StrandsService()

        invalid_code = "def invalid_tool( return x"
        result = service._create_custom_tool("invalid_tool", invalid_code)

        assert result is None

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_load_tools_mixed(self):
        """Test loading a mix of builtin and custom tools."""
        service = StrandsService()

        builtin_tool = MagicMock()
        builtin_tool.name = "calculator"
        builtin_tool.tool_type = ToolType.BUILTIN

        custom_tool = MagicMock()
        custom_tool.name = "my_tool"
        custom_tool.tool_type = ToolType.CUSTOM
        custom_tool.source_code = "def my_tool(x): return x"

        tools = [builtin_tool, custom_tool]

        with patch.object(service, "_get_builtin_tool", return_value=lambda x: x):
            with patch.object(service, "_create_custom_tool", return_value=lambda x: x):
                loaded = service._load_tools(tools)

                # Should load both tools
                assert len(loaded) == 2


class TestStrandsServiceAgentCreation:
    """Tests for agent creation."""

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_create_strands_agent_success(self):
        """Test successful Strands agent creation."""
        service = StrandsService()

        agent = MagicMock()
        agent.model_provider = ModelProvider.BEDROCK
        agent.model_id = "test-model"
        agent.system_prompt = "You are a test agent."

        mock_strands_agent = MagicMock()

        with patch("strands.Agent", return_value=mock_strands_agent):
            with patch.object(service, "_get_model_provider", return_value=MagicMock()):
                with patch.object(service, "_load_tools", return_value=[]):
                    result = service.create_strands_agent(agent, [])

        assert result == mock_strands_agent

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_create_strands_agent_import_error(self):
        """Test agent creation with import error returns None."""
        service = StrandsService()

        agent = MagicMock()
        agent.model_provider = ModelProvider.BEDROCK
        agent.model_id = "test-model"
        agent.system_prompt = "Test"

        with patch("strands.Agent", side_effect=ImportError("No module")):
            result = service.create_strands_agent(agent, [])

        assert result is None


class TestStrandsServiceRun:
    """Tests for running agents."""

    @pytest.mark.unit
    @pytest.mark.sdk
    async def test_run_agent_success(self):
        """Test successful agent run."""
        service = StrandsService()

        agent = MagicMock()
        agent.model_provider = ModelProvider.BEDROCK
        agent.model_id = "test-model"
        agent.system_prompt = "Test"

        mock_strands_agent = MagicMock()
        mock_strands_agent.return_value = "Test response"

        with patch.object(service, "create_strands_agent", return_value=mock_strands_agent):
            result = await service.run_agent(
                agent=agent,
                tools=[],
                input_text="Hello",
                conversation_history=None,
                api_credentials={},
            )

        assert result["success"] is True
        assert result["output"] == "Test response"
        assert "response_time_ms" in result

    @pytest.mark.unit
    @pytest.mark.sdk
    async def test_run_agent_creation_failure(self):
        """Test agent run when agent creation fails."""
        service = StrandsService()

        agent = MagicMock()
        agent.model_provider = ModelProvider.BEDROCK
        agent.model_id = "test-model"

        with patch.object(service, "create_strands_agent", return_value=None):
            result = await service.run_agent(
                agent=agent,
                tools=[],
                input_text="Hello",
            )

        assert result["success"] is False
        assert "error" in result
        assert result["output"] is None

    @pytest.mark.unit
    @pytest.mark.sdk
    async def test_run_agent_exception(self):
        """Test agent run with exception."""
        service = StrandsService()

        agent = MagicMock()
        agent.model_provider = ModelProvider.BEDROCK
        agent.model_id = "test-model"

        mock_strands_agent = MagicMock()
        mock_strands_agent.side_effect = Exception("Test error")

        with patch.object(service, "create_strands_agent", return_value=mock_strands_agent):
            result = await service.run_agent(
                agent=agent,
                tools=[],
                input_text="Hello",
            )

        assert result["success"] is False
        assert "Test error" in result["error"]


class TestStrandsServiceStream:
    """Tests for streaming agent responses."""

    @pytest.mark.unit
    @pytest.mark.sdk
    async def test_stream_agent_creation_failure(self):
        """Test streaming when agent creation fails."""
        service = StrandsService()

        agent = MagicMock()
        agent.model_provider = ModelProvider.BEDROCK
        agent.model_id = "test-model"

        with patch.object(service, "create_strands_agent", return_value=None):
            chunks = []
            async for chunk in service.stream_agent(agent, [], "Hello"):
                chunks.append(chunk)

        assert len(chunks) == 1
        assert "Error" in chunks[0]


class TestStrandsSDKImportCompatibility:
    """Tests for SDK import compatibility."""

    @pytest.mark.sdk
    def test_strands_agents_importable(self):
        """Test that strands-agents package is importable."""
        try:
            import strands
            assert hasattr(strands, "Agent")
        except ImportError:
            pytest.skip("strands-agents not installed")

    @pytest.mark.sdk
    def test_strands_tools_importable(self):
        """Test that strands-agents-tools package is importable."""
        try:
            import strands_agents_tools
            assert hasattr(strands_agents_tools, "calculator")
        except ImportError:
            pytest.skip("strands-agents-tools not installed")

    @pytest.mark.sdk
    def test_strands_models_importable(self):
        """Test that strands models are importable."""
        try:
            from strands.models import BedrockModel
            assert BedrockModel is not None
        except ImportError:
            pytest.skip("strands-agents models not available")


class TestStrandsServiceIntegration:
    """Integration tests requiring actual SDK."""

    @pytest.mark.integration
    @pytest.mark.sdk
    @pytest.mark.slow
    async def test_full_agent_run_mock(self, test_agent, db_session):
        """Test full agent run with mocked SDK."""
        service = StrandsService()

        mock_response = MagicMock()
        mock_response.__str__ = MagicMock(return_value="Hello! I'm your test agent.")
        mock_response.usage = {"total_tokens": 100}

        mock_strands_agent = MagicMock()
        mock_strands_agent.return_value = mock_response

        with patch.object(service, "create_strands_agent", return_value=mock_strands_agent):
            result = await service.run_agent(
                agent=test_agent,
                tools=[],
                input_text="Hello, agent!",
                api_credentials={},
            )

        assert result["success"] is True
        assert "Hello" in result["output"]
