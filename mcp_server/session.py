from dataclasses import dataclass
from datetime import UTC, datetime

HARDCODED_OTP = "9632"
AUTH_REQUIRED_RESPONSE = {
    "error": "AUTH_REQUIRED",
    "message": "Please authenticate first using client_id and OTP",
}
DEFAULT_SESSION_ID = "local-default-session"


@dataclass(frozen=True)
class ClientSession:
    client_id: str
    authenticated_at: datetime


class SessionStore:
    """In-memory session storage.

    Production replacement points:
    - Validate OTPs with a real OTP provider instead of the hardcoded value.
    - Load client/user mappings from a database.
    - Bind session IDs to Microsoft Entra ID tokens or Teams user identity.
    - Store sessions in Redis or another shared store for multi-process deployments.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ClientSession] = {}

    def authenticate(self, session_id: str, client_id: str, otp: str) -> dict:
        # Replace this hardcoded OTP check with real OTP validation later.
        if otp != HARDCODED_OTP:
            return {"authenticated": False, "message": "Invalid OTP"}

        self._sessions[session_id] = ClientSession(
            client_id=client_id,
            authenticated_at=datetime.now(UTC),
        )
        return {
            "authenticated": True,
            "client_id": client_id,
            "message": "Authentication successful",
        }

    def get_client_id(self, session_id: str) -> str | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        return session.client_id

    def clear(self) -> None:
        self._sessions.clear()


def resolve_session_id(headers: dict[str, str] | None = None) -> str:
    headers = headers or {}
    return (
        headers.get("x-mcp-session-id")
        or headers.get("mcp-session-id")
        or headers.get("X-MCP-Session-ID")
        or headers.get("Mcp-Session-Id")
        or DEFAULT_SESSION_ID
    )
