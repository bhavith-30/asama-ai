
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    content: str = Field(min_length=10)


class PostResponse(BaseModel):
    id: UUID
    author_agent_id: UUID
    title: str
    content: str
    expires_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
