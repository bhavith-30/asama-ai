
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.database.connection import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    company_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=True
    )

    industry_category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    webhook_url: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    interest_manifesto: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    interest_embedding = mapped_column(
        Vector(384), nullable=True
    )

    trust_score: Mapped[float] = mapped_column(
        Float, default=1.0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
