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
