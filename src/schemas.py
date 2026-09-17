from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TicketCreate(BaseModel):
    message: str = Field(min_length=1)


class DecisionResponse(BaseModel):
    action: str
    reason: str
    confidence: float
    sources: list[str]


class TicketResponse(BaseModel):
    id: int
    message: str
    created_at: datetime
    decision: DecisionResponse | None = None

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str