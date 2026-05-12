from fastapi import APIRouter, HTTPException, Path

from mock_backend.models import BasicInfoField, BasicInfoResponse, OnboardingStatusResponse

router = APIRouter()

CLIENT_BASIC_INFO = {
    BasicInfoField.name: "John",
    BasicInfoField.family: "Doe",
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
        value=CLIENT_BASIC_INFO[parsed_field],
    )
