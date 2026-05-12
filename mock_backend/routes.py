from fastapi import APIRouter, HTTPException, Path

from mock_backend.models import (
    BasicInfoField,
    BasicInfoResponse,
    ClientFacilityResponse,
    OnboardingStatusResponse,
    OutreachItem,
    OutreachSummaryResponse,
)

router = APIRouter()

CLIENTS = {
    "123": {
        "name": "John",
        "family": "Doe",
        "facility_limit_eur": 75_000_000,
        "outreaches": [
            {
                "outreach_id": "out-123-001",
                "date": "2026-04-22",
                "channel": "Email",
                "reason": "Annual facility review",
                "questions_to_answer": [
                    "Can you confirm the latest audited revenue?",
                    "Do you expect the current facility usage to increase next quarter?",
                    "Should the facility maturity date remain unchanged?",
                ],
            },
            {
                "outreach_id": "out-123-002",
                "date": "2026-05-03",
                "channel": "Teams",
                "reason": "Updated cash-flow forecast",
                "questions_to_answer": [
                    "Can you provide the revised 12-month cash-flow forecast?",
                    "Are there any expected covenant changes?",
                ],
            },
        ],
    },
    "456": {
        "name": "Alice",
        "family": "Smith",
        "facility_limit_eur": 12_500_000,
        "outreaches": [
            {
                "outreach_id": "out-456-001",
                "date": "2026-03-18",
                "channel": "Phone",
                "reason": "New working-capital request",
                "questions_to_answer": [
                    "What is the requested seasonal working-capital amount?",
                    "Which invoices support the drawdown request?",
                ],
            },
            {
                "outreach_id": "out-456-002",
                "date": "2026-04-09",
                "channel": "Email",
                "reason": "Collateral documentation update",
                "questions_to_answer": [
                    "Can you upload the latest inventory report?",
                    "Has any pledged collateral been sold or replaced?",
                    "Who should sign the updated collateral schedule?",
                ],
            },
        ],
    },
    "789": {
        "name": "Maria",
        "family": "Garcia",
        "facility_limit_eur": 200_000_000,
        "outreaches": [
            {
                "outreach_id": "out-789-001",
                "date": "2026-02-28",
                "channel": "Email",
                "reason": "Syndicated facility renewal",
                "questions_to_answer": [
                    "Do you want to renew the syndicated facility at the current limit?",
                    "Should new participating banks be invited?",
                    "Can you share the board approval timeline?",
                ],
            },
            {
                "outreach_id": "out-789-002",
                "date": "2026-04-17",
                "channel": "Meeting",
                "reason": "ESG reporting requirement",
                "questions_to_answer": [
                    "Can you provide the latest emissions report?",
                    "Which sustainability KPIs should be linked to margin adjustments?",
                ],
            },
            {
                "outreach_id": "out-789-003",
                "date": "2026-05-06",
                "channel": "Teams",
                "reason": "Large drawdown notification",
                "questions_to_answer": [
                    "What is the expected drawdown date?",
                    "What business purpose should be recorded for the drawdown?",
                ],
            },
        ],
    },
}


@router.get("/status/{client_id}", response_model=OnboardingStatusResponse, tags=["mock-backend"])
async def get_status(
    client_id: str = Path(..., min_length=1, description="Client identifier."),
) -> OnboardingStatusResponse:
    return OnboardingStatusResponse(client_id=client_id)


@router.get("/info/{client_id}/{field}", response_model=BasicInfoResponse, tags=["mock-backend"])
async def get_info(
    client_id: str = Path(..., min_length=1, description="Client identifier."),
    field: str = Path(..., description="Allowed values are name or family."),
) -> BasicInfoResponse:
    try:
        parsed_field = BasicInfoField(field)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_field",
                "message": "Allowed fields are name and family.",
                "allowed_fields": ["name", "family"],
            },
        ) from exc

    return BasicInfoResponse(
        client_id=client_id,
        field=parsed_field,
        value=_get_client(client_id)[parsed_field.value],
    )


@router.get("/facility/{client_id}", response_model=ClientFacilityResponse, tags=["mock-backend"])
async def get_facility(
    client_id: str = Path(..., min_length=1, description="Client identifier."),
) -> ClientFacilityResponse:
    client = _get_client(client_id)
    facility_limit_eur = client["facility_limit_eur"]
    return ClientFacilityResponse(
        client_id=client_id,
        client_name=_client_name(client),
        facility_limit_eur=facility_limit_eur,
        formatted_limit=f"EUR {facility_limit_eur:,}",
    )


@router.get("/outreach/{client_id}/summary", response_model=OutreachSummaryResponse, tags=["mock-backend"])
async def summarize_outreach(
    client_id: str = Path(..., min_length=1, description="Client identifier."),
) -> OutreachSummaryResponse:
    client = _get_client(client_id)
    outreaches = [OutreachItem.model_validate(item) for item in client["outreaches"]]
    reasons = [item.reason for item in outreaches]
    questions_count = sum(len(item.questions_to_answer) for item in outreaches)
    highlights = [
        f"{item.date} via {item.channel}: {item.reason}; {len(item.questions_to_answer)} questions to answer."
        for item in outreaches
    ]
    summary = (
        f"{_client_name(client)} has {len(outreaches)} outreach items. "
        f"Reasons: {', '.join(reasons)}. "
        f"You should answer {questions_count} questions in total."
    )
    return OutreachSummaryResponse(
        client_id=client_id,
        client_name=_client_name(client),
        outreach_count=len(outreaches),
        questions_to_answer_count=questions_count,
        reasons=reasons,
        highlights=highlights,
        summary=summary,
        outreaches=outreaches,
    )


def _get_client(client_id: str) -> dict:
    if client_id in CLIENTS:
        return CLIENTS[client_id]
    return CLIENTS["123"]


def _client_name(client: dict) -> str:
    return f"{client['name']} {client['family']}"
