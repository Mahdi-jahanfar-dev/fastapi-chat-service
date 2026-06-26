"""
Single import point for all ORM models.

Used in alembic/env.py:

    from infrastructure.database import models  # noqa: F401
    from infrastructure.database.base import Base
    target_metadata = Base.metadata
"""

from infrastructure.database.base import Base  # noqa: F401
from infrastructure.database.user import UserORM, ContactORM  # noqa: F401
from infrastructure.database.chat import ChatORM, ChatMemberORM  # noqa: F401
from infrastructure.database.message import MessageORM, MessageReadStatusORM  # noqa: F401

__all__ = [
    "Base",
    "UserORM",
    "ContactORM",
    "ChatORM",
    "ChatMemberORM",
    "MessageORM",
    "MessageReadStatusORM",
]