import pytest
from httpx import ASGITransport, AsyncClient

from mcp_server.app import create_app
from mcp_server.config import Settings
from mcp_server.models import (
    BasicInfoField,
    BasicInfoResponse,
    ClientFacilityResponse,
    OnboardingStatusResponse,
    OutreachItem,
    OutreachSummaryResponse,
)
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

    async def get_client_facility(self, client_id: str) -> ClientFacilityResponse:
        return ClientFacilityResponse(
            client_id=client_id,
            client_name="John Doe",
            facility_limit_eur=75_000_000,
            formatted_limit="EUR 75,000,000",
        )

    async def summarize_client_outreach(self, client_id: str) -> OutreachSummaryResponse:
        outreaches = [
            OutreachItem(
                outreach_id="out-123-001",
                date="2026-04-22",
                channel="Email",
                reason="Annual facility review",
                questions_to_answer=[
                    "Can you confirm the latest audited revenue?",
                    "Do you expect the current facility usage to increase next quarter?",
                ],
            ),
            OutreachItem(
                outreach_id="out-123-002",
                date="2026-05-03",
                channel="Teams",
                reason="Updated cash-flow forecast",
                questions_to_answer=["Can you provide the revised 12-month cash-flow forecast?"],
            ),
        ]
        return OutreachSummaryResponse(
            client_id=client_id,
            client_name="John Doe",
            outreach_count=2,
            questions_to_answer_count=3,
            reasons=["Annual facility review", "Updated cash-flow forecast"],
            highlights=[
                "2026-04-22 via Email: Annual facility review; 2 questions to answer.",
                "2026-05-03 via Teams: Updated cash-flow forecast; 1 questions to answer.",
            ],
            summary="John Doe has 2 outreach items. Reasons: Annual facility review, Updated cash-flow forecast. You should answer 3 questions in total.",
            outreaches=outreaches,
        )

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
