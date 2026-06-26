from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class for all ORM models.

    AsyncAttrs enables awaiting lazy relationships in async context:
        members = await chat.awaitable_attrs.members
    """
    pass


class TimestampMixin:
    """
    Adds created_at and updated_at to any ORM model that inherits it.
    Both columns are timezone-aware and managed by the DB server.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )