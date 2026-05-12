from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class BasicInfoField(StrEnum):
    name = "name"
    family = "family"


class OnboardingStatusArguments(BaseModel):
    client_id: str = Field(..., min_length=1, examples=["123"])


class BasicInfoArguments(BaseModel):
    client_id: str = Field(..., min_length=1, examples=["123"])
    field: BasicInfoField = Field(..., description="Allowed values are name or family.")


class OnboardingStatusResponse(BaseModel):
    client_id: str = Field(..., examples=["123"])
    status: str = Field(..., examples=["Completed"])
    message: str = Field(..., examples=["Client onboarding completed successfully"])


class BasicInfoResponse(BaseModel):
    client_id: str = Field(..., examples=["123"])
    field: BasicInfoField = Field(..., examples=["name"])
    value: str = Field(..., examples=["John"])


class ToolMetadata(BaseModel):
    name: str
    description: str
    inputSchema: dict[str, Any]


class ToolListResponse(BaseModel):
    tools: list[ToolMetadata]


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Any | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorBody
