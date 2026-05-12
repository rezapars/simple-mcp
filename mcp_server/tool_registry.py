from copy import deepcopy
from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from mcp_server.backend_client import BackendClient
from mcp_server.errors import BackendClientError, ToolExecutionError
from mcp_server.models import (
    BasicInfoArguments,
    ClientFacilityArguments,
    OnboardingStatusArguments,
    OutreachSummaryArguments,
)


TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_client_onboarding_status",
        "description": "Get the onboarding status for a client by client ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "Client identifier, for example 123.",
                    "minLength": 1,
                }
            },
            "required": ["client_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_client_basic_info",
        "description": "Get a client's basic name or family value by client ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "Client identifier, for example 123.",
                    "minLength": 1,
                },
                "field": {
                    "type": "string",
                    "description": "Basic info field to retrieve.",
                    "enum": ["name", "family"],
                },
            },
            "required": ["client_id", "field"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_client_facility_limit",
        "description": "Get the current facility limit in EUR and client name for a client ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "Client identifier, for example 123.",
                    "minLength": 1,
                }
            },
            "required": ["client_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "summarize_client_outreach",
        "description": (
            "Summarize outreach highlights for a client, including outreach reasons "
            "and how many questions should be answered."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "Client identifier, for example 123.",
                    "minLength": 1,
                }
            },
            "required": ["client_id"],
            "additionalProperties": False,
        },
    },
]


def list_tools() -> list[dict[str, Any]]:
    return deepcopy(TOOLS)


async def call_tool(
    name: str,
    arguments: dict[str, Any] | None,
    backend_client: BackendClient,
) -> dict[str, Any]:
    arguments = arguments or {}

    try:
        if name == "get_client_onboarding_status":
            parsed = OnboardingStatusArguments.model_validate(arguments)
            result = await backend_client.get_status(parsed.client_id)
            return result.model_dump(mode="json")

        if name == "get_client_basic_info":
            parsed = BasicInfoArguments.model_validate(arguments)
            result = await backend_client.get_basic_info(parsed.client_id, parsed.field)
            return result.model_dump(mode="json")

        if name == "get_client_facility_limit":
            parsed = ClientFacilityArguments.model_validate(arguments)
            result = await backend_client.get_client_facility(parsed.client_id)
            return result.model_dump(mode="json")

        if name == "summarize_client_outreach":
            parsed = OutreachSummaryArguments.model_validate(arguments)
            result = await backend_client.summarize_client_outreach(parsed.client_id)
            return result.model_dump(mode="json")

    except ValidationError as exc:
        raise ToolExecutionError(
            code="invalid_arguments",
            message="Tool arguments failed validation.",
            status_code=400,
            details=jsonable_encoder(exc.errors()),
        ) from exc
    except BackendClientError as exc:
        raise ToolExecutionError(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        ) from exc

    raise ToolExecutionError(
        code="tool_not_found",
        message=f"Unknown tool: {name}",
        status_code=404,
    )
