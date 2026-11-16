
from uuid import UUID

from pydantic import BaseModel, EmailStr, HttpUrl, Field, ConfigDict


class AgentRegister(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)
    industry_category: str = Field(min_length=2, max_length=100)
    webhook_url: HttpUrl
    interest_manifesto: str = Field(min_length=10)


class AgentResponse(BaseModel):
    id: UUID
    company_name: str
    email: str
    industry_category: str
    webhook_url: str
    interest_manifesto: str
    trust_score: float

    model_config = ConfigDict(from_attributes=True)

class AgentLogin(BaseModel):
    email: EmailStr
    password: str
