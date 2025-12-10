import asyncio
from datetime import datetime
from typing import AsyncGenerator, Optional, Dict, Any, List
import structlog

from app.models.agent import Agent, AgentRun, RunStatus, ModelProvider
from app.models.tool import Tool, ToolType

logger = structlog.get_logger()


class StrandsService:
    """Service for interacting with Strands Agents SDK"""

    def __init__(self):
        self._agents_cache: Dict[int, Any] = {}

    def _get_model_provider(self, agent: Agent, api_credentials: Dict[str, str] = None):
        """Get the appropriate model provider based on agent configuration"""
        try:
            if agent.model_provider == ModelProvider.BEDROCK:
                from strands.models import BedrockModel
                return BedrockModel(
                    model_id=agent.model_id,
                    region_name=api_credentials.get("aws_region", "us-east-1") if api_credentials else "us-east-1",
                )
            elif agent.model_provider == ModelProvider.OLLAMA:
                from strands.models import OllamaModel
                return OllamaModel(
                    model_id=agent.model_id,
                    host=api_credentials.get("ollama_host", "http://localhost:11434") if api_credentials else "http://localhost:11434",
                )
            elif agent.model_provider == ModelProvider.ANTHROPIC:
                from strands.models import AnthropicModel
                return AnthropicModel(
                    model_id=agent.model_id,
                    api_key=api_credentials.get("api_key") if api_credentials else None,
                )
            elif agent.model_provider == ModelProvider.OPENAI:
                from strands.models import OpenAIModel
                return OpenAIModel(
                    model_id=agent.model_id,
                    api_key=api_credentials.get("api_key") if api_credentials else None,
                )
            else:
                # Default to Bedrock
                from strands.models import BedrockModel
                return BedrockModel(model_id=agent.model_id)
        except ImportError as e:
            logger.warning("strands_sdk_import_error", error=str(e))
            return None

    def _load_tools(self, tools: List[Tool]) -> List[Any]:
        """Load tools for the agent"""
        loaded_tools = []

        for tool in tools:
            try:
                if tool.tool_type == ToolType.BUILTIN:
                    # Import from strands-agents-tools
                    tool_func = self._get_builtin_tool(tool.name)
                    if tool_func:
                        loaded_tools.append(tool_func)
                elif tool.tool_type == ToolType.CUSTOM and tool.source_code:
                    # Execute custom tool code
                    tool_func = self._create_custom_tool(tool.name, tool.source_code)
                    if tool_func:
                        loaded_tools.append(tool_func)
            except Exception as e:
                logger.error("tool_load_error", tool_name=tool.name, error=str(e))

        return loaded_tools

    def _get_builtin_tool(self, tool_name: str):
        """Get a built-in tool from strands-agents-tools"""
        try:
            if tool_name == "calculator":
                from strands_agents_tools import calculator
                return calculator
            elif tool_name == "http_request":
                from strands_agents_tools import http_request
                return http_request
            elif tool_name == "file_read":
                from strands_agents_tools import file_read
                return file_read
            elif tool_name == "file_write":
                from strands_agents_tools import file_write
                return file_write
            elif tool_name == "shell":
                from strands_agents_tools import shell
                return shell
            elif tool_name == "python_repl":
                from strands_agents_tools import python_repl
                return python_repl
        except ImportError as e:
            logger.warning("builtin_tool_import_error", tool=tool_name, error=str(e))
        return None

    def _create_custom_tool(self, name: str, source_code: str):
        """Create a custom tool from source code"""
        try:
            # Create a namespace for the tool
            namespace = {}
            exec(source_code, namespace)

            # Look for a function with the tool name or decorated with @tool
            if name in namespace and callable(namespace[name]):
                return namespace[name]

            # Look for any function decorated with @tool
            for item in namespace.values():
                if callable(item) and hasattr(item, "_is_tool"):
                    return item

        except Exception as e:
            logger.error("custom_tool_creation_error", name=name, error=str(e))
        return None

    def create_strands_agent(
        self,
        agent: Agent,
        tools: List[Tool],
        api_credentials: Dict[str, str] = None
    ):
        """Create a Strands Agent instance"""
        try:
            from strands import Agent as StrandsAgent

            model = self._get_model_provider(agent, api_credentials)
            loaded_tools = self._load_tools(tools)

            strands_agent = StrandsAgent(
                model=model,
                tools=loaded_tools if loaded_tools else None,
                system_prompt=agent.system_prompt or "",
            )

            return strands_agent

        except ImportError as e:
            logger.error("strands_import_error", error=str(e))
            return None
        except Exception as e:
            logger.error("agent_creation_error", error=str(e))
            return None

    async def run_agent(
        self,
        agent: Agent,
        tools: List[Tool],
        input_text: str,
        conversation_history: List[Dict] = None,
        api_credentials: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Run the agent and return the response"""
        start_time = datetime.utcnow()

        try:
            strands_agent = self.create_strands_agent(agent, tools, api_credentials)

            if strands_agent is None:
                return {
                    "success": False,
                    "error": "Failed to create agent. Please check your configuration and API credentials.",
                    "output": None,
                }

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: strands_agent(input_text)
            )

            end_time = datetime.utcnow()
            response_time = int((end_time - start_time).total_seconds() * 1000)

            return {
                "success": True,
                "output": str(response),
                "response_time_ms": response_time,
                "tokens_used": getattr(response, "usage", {}).get("total_tokens"),
            }

        except Exception as e:
            logger.error("agent_run_error", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "output": None,
            }

    async def stream_agent(
        self,
        agent: Agent,
        tools: List[Tool],
        input_text: str,
        conversation_history: List[Dict] = None,
        api_credentials: Dict[str, str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream the agent response"""
        try:
            strands_agent = self.create_strands_agent(agent, tools, api_credentials)

            if strands_agent is None:
                yield "Error: Failed to create agent"
                return

            # Use streaming if available
            loop = asyncio.get_event_loop()

            def run_with_callback():
                chunks = []
                for chunk in strands_agent.stream(input_text):
                    chunks.append(chunk)
                return chunks

            # For now, run and yield complete response
            # Real streaming would need SDK support
            response = await loop.run_in_executor(None, lambda: strands_agent(input_text))
            yield str(response)

        except Exception as e:
            logger.error("agent_stream_error", error=str(e))
            yield f"Error: {str(e)}"
