"""
Tool management tests for Strands GUI backend.
"""
import pytest
from httpx import AsyncClient
from io import BytesIO

from app.models.tool import Tool, ToolType
from app.models.user import User


class TestToolList:
    """Tests for listing tools."""

    @pytest.mark.integration
    async def test_list_tools_empty(self, authenticated_client: AsyncClient):
        """Test listing tools when none exist."""
        response = await authenticated_client.get("/api/tools")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.integration
    async def test_list_tools_with_custom(
        self,
        authenticated_client: AsyncClient,
        test_tool: Tool
    ):
        """Test listing tools with custom tool."""
        response = await authenticated_client.get("/api/tools")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        tool_names = [t["name"] for t in data]
        assert test_tool.name in tool_names

    @pytest.mark.integration
    async def test_list_tools_includes_global(
        self,
        authenticated_client: AsyncClient,
        builtin_tool: Tool
    ):
        """Test that global/builtin tools are included in list."""
        response = await authenticated_client.get("/api/tools")

        assert response.status_code == 200
        data = response.json()
        tool_names = [t["name"] for t in data]
        assert builtin_tool.name in tool_names

    @pytest.mark.integration
    async def test_list_tools_unauthorized(self, client: AsyncClient):
        """Test listing tools without authentication fails."""
        response = await client.get("/api/tools")
        assert response.status_code == 403


class TestListBuiltinTools:
    """Tests for listing builtin tools."""

    @pytest.mark.integration
    async def test_list_builtin_tools(
        self,
        client: AsyncClient,
        builtin_tool: Tool
    ):
        """Test listing builtin tools (no auth required)."""
        response = await client.get("/api/tools/builtin")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestToolCreate:
    """Tests for creating tools."""

    @pytest.mark.integration
    async def test_create_custom_tool(
        self,
        authenticated_client: AsyncClient,
        tool_create_data: dict
    ):
        """Test creating a custom tool."""
        response = await authenticated_client.post(
            "/api/tools",
            json=tool_create_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == tool_create_data["name"]
        assert data["display_name"] == tool_create_data["display_name"]
        assert data["tool_type"] == "custom"
        assert data["source_code"] == tool_create_data["source_code"]

    @pytest.mark.integration
    async def test_create_tool_minimal(self, authenticated_client: AsyncClient):
        """Test creating a tool with minimal data."""
        response = await authenticated_client.post(
            "/api/tools",
            json={
                "name": "minimal_tool",
                "display_name": "Minimal Tool",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "minimal_tool"
        assert data["is_global"] is False

    @pytest.mark.integration
    async def test_create_tool_invalid_name(self, authenticated_client: AsyncClient):
        """Test creating a tool with empty name fails."""
        response = await authenticated_client.post(
            "/api/tools",
            json={
                "name": "",
                "display_name": "Some Tool",
            },
        )

        assert response.status_code == 422

    @pytest.mark.integration
    async def test_create_tool_unauthorized(self, client: AsyncClient):
        """Test creating a tool without authentication fails."""
        response = await client.post(
            "/api/tools",
            json={
                "name": "unauthorized_tool",
                "display_name": "Unauthorized Tool",
            },
        )
        assert response.status_code == 403


class TestToolGet:
    """Tests for getting individual tools."""

    @pytest.mark.integration
    async def test_get_tool(
        self,
        authenticated_client: AsyncClient,
        test_tool: Tool
    ):
        """Test getting a tool by ID."""
        response = await authenticated_client.get(f"/api/tools/{test_tool.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_tool.id
        assert data["name"] == test_tool.name

    @pytest.mark.integration
    async def test_get_builtin_tool(
        self,
        authenticated_client: AsyncClient,
        builtin_tool: Tool
    ):
        """Test getting a builtin tool by ID."""
        response = await authenticated_client.get(f"/api/tools/{builtin_tool.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == builtin_tool.id
        assert data["is_global"] is True

    @pytest.mark.integration
    async def test_get_tool_not_found(self, authenticated_client: AsyncClient):
        """Test getting a non-existent tool returns 404."""
        response = await authenticated_client.get("/api/tools/99999")

        assert response.status_code == 404


class TestToolUpdate:
    """Tests for updating tools."""

    @pytest.mark.integration
    async def test_update_tool_name(
        self,
        authenticated_client: AsyncClient,
        test_tool: Tool
    ):
        """Test updating a tool's name."""
        response = await authenticated_client.put(
            f"/api/tools/{test_tool.id}",
            json={"name": "updated_tool_name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated_tool_name"

    @pytest.mark.integration
    async def test_update_tool_description(
        self,
        authenticated_client: AsyncClient,
        test_tool: Tool
    ):
        """Test updating a tool's description."""
        response = await authenticated_client.put(
            f"/api/tools/{test_tool.id}",
            json={"description": "Updated description"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    @pytest.mark.integration
    async def test_update_tool_source_code(
        self,
        authenticated_client: AsyncClient,
        test_tool: Tool
    ):
        """Test updating a tool's source code."""
        new_code = """
def updated_tool(x: str) -> str:
    return f"Updated: {x}"
"""
        response = await authenticated_client.put(
            f"/api/tools/{test_tool.id}",
            json={"source_code": new_code},
        )

        assert response.status_code == 200
        data = response.json()
        assert "updated_tool" in data["source_code"]

    @pytest.mark.integration
    async def test_update_tool_not_found(self, authenticated_client: AsyncClient):
        """Test updating a non-existent tool returns 404."""
        response = await authenticated_client.put(
            "/api/tools/99999",
            json={"name": "updated"},
        )

        assert response.status_code == 404

    @pytest.mark.integration
    async def test_update_global_tool_forbidden(
        self,
        authenticated_client: AsyncClient,
        builtin_tool: Tool
    ):
        """Test that updating a global tool is forbidden."""
        response = await authenticated_client.put(
            f"/api/tools/{builtin_tool.id}",
            json={"name": "hacked_calculator"},
        )

        assert response.status_code == 403


class TestToolDelete:
    """Tests for deleting tools."""

    @pytest.mark.integration
    async def test_delete_tool(
        self,
        authenticated_client: AsyncClient,
        test_tool: Tool
    ):
        """Test deleting a custom tool."""
        response = await authenticated_client.delete(f"/api/tools/{test_tool.id}")

        assert response.status_code == 204

        # Verify tool is deleted
        get_response = await authenticated_client.get(f"/api/tools/{test_tool.id}")
        assert get_response.status_code == 404

    @pytest.mark.integration
    async def test_delete_tool_not_found(self, authenticated_client: AsyncClient):
        """Test deleting a non-existent tool returns 404."""
        response = await authenticated_client.delete("/api/tools/99999")

        assert response.status_code == 404

    @pytest.mark.integration
    async def test_delete_global_tool_forbidden(
        self,
        authenticated_client: AsyncClient,
        builtin_tool: Tool
    ):
        """Test that deleting a global tool is forbidden."""
        response = await authenticated_client.delete(f"/api/tools/{builtin_tool.id}")

        assert response.status_code == 403


class TestToolUpload:
    """Tests for uploading tools as files."""

    @pytest.mark.integration
    async def test_upload_python_file(self, authenticated_client: AsyncClient):
        """Test uploading a Python file as a tool."""
        python_code = b'''
from strands.tools import tool

@tool
def my_uploaded_tool(input: str) -> str:
    """A tool uploaded from a file."""
    return f"Processed: {input}"
'''
        # Create file-like object
        files = {"file": ("my_tool.py", python_code, "text/x-python")}
        response = await authenticated_client.post(
            "/api/tools/upload",
            files=files,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "my_tool"
        assert "my_uploaded_tool" in data["source_code"]

    @pytest.mark.integration
    async def test_upload_non_python_file_fails(self, authenticated_client: AsyncClient):
        """Test uploading a non-Python file fails."""
        files = {"file": ("config.json", b'{"key": "value"}', "application/json")}
        response = await authenticated_client.post(
            "/api/tools/upload",
            files=files,
        )

        assert response.status_code == 400
        assert "python" in response.json()["detail"].lower()


class TestToolValidation:
    """Tests for tool source code validation."""

    @pytest.mark.integration
    async def test_validate_valid_code(self, authenticated_client: AsyncClient):
        """Test validating valid Python code."""
        response = await authenticated_client.post(
            "/api/tools/validate",
            json={
                "name": "test",
                "display_name": "Test",
                "source_code": "def my_tool(x): return x * 2",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True

    @pytest.mark.integration
    async def test_validate_invalid_syntax(self, authenticated_client: AsyncClient):
        """Test validating code with syntax errors."""
        response = await authenticated_client.post(
            "/api/tools/validate",
            json={
                "name": "test",
                "display_name": "Test",
                "source_code": "def my_tool(x) return x",  # Missing colon
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "syntax" in data["message"].lower()

    @pytest.mark.integration
    async def test_validate_empty_code(self, authenticated_client: AsyncClient):
        """Test validating empty source code."""
        response = await authenticated_client.post(
            "/api/tools/validate",
            json={
                "name": "test",
                "display_name": "Test",
                "source_code": "",
            },
        )

        # Empty string should fail validation (requires source code)
        assert response.status_code == 400


class TestToolOwnership:
    """Tests for tool ownership and access control."""

    @pytest.mark.integration
    async def test_cannot_see_other_user_tools(
        self,
        client: AsyncClient,
        db_session,
        test_tool: Tool
    ):
        """Test that users cannot see other users' custom tools."""
        from app.core.security import create_access_token, get_password_hash
        from app.models.user import User

        # Create another user
        other_user = User(
            email="other_tool_user@example.com",
            hashed_password=get_password_hash("otherpassword"),
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        token = create_access_token(data={"sub": str(other_user.id)})
        client.headers["Authorization"] = f"Bearer {token}"

        # Other user should not see the test_tool in their list
        response = await client.get("/api/tools")
        assert response.status_code == 200
        data = response.json()
        tool_ids = [t["id"] for t in data if not t["is_global"]]
        assert test_tool.id not in tool_ids

    @pytest.mark.integration
    async def test_cannot_delete_other_user_tool(
        self,
        client: AsyncClient,
        db_session,
        test_tool: Tool
    ):
        """Test that users cannot delete other users' tools."""
        from app.core.security import create_access_token, get_password_hash
        from app.models.user import User

        # Create another user
        other_user = User(
            email="other_delete_user@example.com",
            hashed_password=get_password_hash("otherpassword"),
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        token = create_access_token(data={"sub": str(other_user.id)})
        client.headers["Authorization"] = f"Bearer {token}"

        # Should get 404 (not found for this user)
        response = await client.delete(f"/api/tools/{test_tool.id}")
        assert response.status_code == 404
