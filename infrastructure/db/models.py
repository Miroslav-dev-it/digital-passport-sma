"""SQLAlchemy ORM models for persistence."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base."""


class TimestampMixin:
    """Common timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class GenerationLog(Base, TimestampMixin):
    """Top-level log about a generation request."""

    __tablename__ = "generation_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prompt_hash: Mapped[str] = mapped_column(String(64), index=True)
    language: Mapped[str] = mapped_column(String(32), index=True)
    model: Mapped[str] = mapped_column(String(64))
    tokens_in: Mapped[int] = mapped_column(Integer)
    tokens_out: Mapped[int] = mapped_column(Integer)
    rb_flags: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class GenerationArtifact(Base, TimestampMixin):
    """Stores generated code artifacts."""

    __tablename__ = "generation_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    log_id: Mapped[str] = mapped_column(String(36), index=True)
    language: Mapped[str] = mapped_column(String(32))
    code: Mapped[str] = mapped_column(Text)
