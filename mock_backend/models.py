from enum import StrEnum

from pydantic import BaseModel, Field


class BasicInfoField(StrEnum):
    name = "name"
    family = "family"


class OnboardingStatusResponse(BaseModel):
    client_id: str = Field(..., examples=["123"])
    status: str = Field(default="Completed", examples=["Completed"])
    message: str = Field(
        default="Client onboarding completed successfully",
        examples=["Client onboarding completed successfully"],
    )


class BasicInfoResponse(BaseModel):
    client_id: str = Field(..., examples=["123"])
    field: BasicInfoField = Field(..., examples=["name"])
    value: str = Field(..., examples=["John"])


class ClientFacilityResponse(BaseModel):
    client_id: str = Field(..., examples=["123"])
    client_name: str = Field(..., examples=["John Doe"])
    facility_limit_eur: int = Field(..., ge=1_000_000, le=200_000_000, examples=[75_000_000])
    currency: str = Field(default="EUR", examples=["EUR"])
    formatted_limit: str = Field(..., examples=["EUR 75,000,000"])


class OutreachItem(BaseModel):
    outreach_id: str = Field(..., examples=["out-123-001"])
    date: str = Field(..., examples=["2026-04-22"])
    channel: str = Field(..., examples=["Email"])
    reason: str = Field(..., examples=["Annual facility review"])
    questions_to_answer: list[str] = Field(..., min_length=1)


class OutreachSummaryResponse(BaseModel):
    client_id: str = Field(..., examples=["123"])
    client_name: str = Field(..., examples=["John Doe"])
    outreach_count: int = Field(..., ge=0, examples=[2])
    questions_to_answer_count: int = Field(..., ge=0, examples=[5])
    reasons: list[str] = Field(..., examples=[["Annual facility review", "Updated revenue forecast"]])
    highlights: list[str] = Field(..., min_length=1)
    summary: str = Field(..., examples=["Client 123 has 2 outreach items and 5 questions to answer."])
    outreaches: list[OutreachItem] = Field(..., min_length=1)
