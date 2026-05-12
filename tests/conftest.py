import pytest
from httpx import ASGITransport, AsyncClient

from mcp_server.app import create_app
from mcp_server.config import Settings
from mcp_server.models import BasicInfoField, BasicInfoResponse, OnboardingStatusResponse
from mock_backend.app import create_app as create_backend_app


class FakeBackendClient:
    async def health(self) -> dict[str, str]:
        return {"status": "ok", "service": "fake-backend"}

    async def get_status(self, client_id: str) -> OnboardingStatusResponse:
        return OnboardingStatusResponse(
            client_id=client_id,
            status="Completed",
            message="Client onboarding completed successfully",
        )

    async def get_basic_info(self, client_id: str, field: BasicInfoField) -> BasicInfoResponse:
        value = "John" if field == BasicInfoField.name else "Doe"
        return BasicInfoResponse(client_id=client_id, field=field, value=value)

    async def close(self) -> None:
        return None


@pytest.fixture
def mcp_app():
    settings = Settings(backend_base_url="http://testserver", auth_required=False)
    app = create_app(settings)
    app.state.backend_client = FakeBackendClient()
    return app


@pytest.fixture
def backend_app():
    return create_backend_app()


@pytest.fixture
async def mcp_client(mcp_app):
    async with AsyncClient(
        transport=ASGITransport(app=mcp_app),
        base_url="http://testserver",
    ) as client:
        yield client


@pytest.fixture
async def backend_client(backend_app):
    async with AsyncClient(
        transport=ASGITransport(app=backend_app),
        base_url="http://testserver",
    ) as client:
        yield client
