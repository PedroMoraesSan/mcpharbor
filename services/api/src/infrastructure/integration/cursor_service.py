import json
from pathlib import Path
from uuid import uuid4

from domain.entities.credential import Integration
from domain.entities.mcp import MCP
from domain.services.integration_service import IntegrationService
from domain.value_objects.enums import IntegrationClient
from infrastructure.mcp.wrapper_command import install_wrapper_script, wrapper_command
from shared.settings import settings
from shared.time import utc_now


class CursorIntegrationService(IntegrationService):
    def __init__(self) -> None:
        self._settings = settings

    async def install_wrapper(self) -> str:
        return install_wrapper_script()

    async def connect_cursor(self, mcp: MCP, credential_keys: list[str] | None = None) -> str:
        await self.install_wrapper()
        command, args = wrapper_command(mcp.catalog_id)
        config_path = self._settings.cursor_config_path
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config = json.loads(config_path.read_text()) if config_path.exists() else {"mcpServers": {}}

        env_key = credential_keys[0] if credential_keys else None
        server_name = mcp.catalog_id
        server_env = {
            "MCPHARBOR_MCP_ID": str(mcp.id),
            "MCPHARBOR_DOCKER_IMAGE": mcp.docker_image,
        }
        if env_key:
            server_env["MCPHARBOR_ENV_KEY"] = env_key
        config["mcpServers"][server_name] = {
            "command": command,
            "args": args,
            "env": server_env,
        }

        config_path.write_text(json.dumps(config, indent=2))
        return str(config_path)

    async def disconnect_cursor(self, mcp: MCP) -> None:
        config_path = self._settings.cursor_config_path
        if not config_path.exists():
            return
        config = json.loads(config_path.read_text())
        servers = config.get("mcpServers", {})
        to_remove = [
            name
            for name, server in servers.items()
            if server.get("env", {}).get("MCPHARBOR_MCP_ID") == str(mcp.id)
            or name == mcp.catalog_id
        ]
        for name in to_remove:
            servers.pop(name, None)
        config_path.write_text(json.dumps(config, indent=2))

    async def is_cursor_connected(self, mcp_id) -> bool:
        config_path = self._settings.cursor_config_path
        if not config_path.exists():
            return False
        config = json.loads(config_path.read_text())
        for _name, server in config.get("mcpServers", {}).items():
            env = server.get("env", {})
            if env.get("MCPHARBOR_MCP_ID") == str(mcp_id):
                return True
        return False

    def create_integration_record(self, mcp: MCP, config_path: str) -> Integration:
        return Integration(
            id=uuid4(),
            client=IntegrationClient.CURSOR,
            mcp_id=mcp.id,
            config_path=config_path,
            connected_at=utc_now(),
        )
