
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CommentCreate(BaseModel):
    content: str = Field(min_length=2)


class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    author_agent_id: UUID
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
