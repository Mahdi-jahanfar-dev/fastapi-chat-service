from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base, TimestampMixin


class MessageStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    DELETED = "deleted"


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    AUDIO = "audio"
    SYSTEM = "system"


class MessageORM(Base, TimestampMixin):
    """
    A single message inside a chat.

    - reply_to_id  : self-referential FK for reply threading
    - media_url    : populated for IMAGE / VIDEO / FILE / AUDIO types
    - status=DELETED means soft-deleted; content should be wiped at app level
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,   # survives user deletion
        index=True,
    )
    reply_to_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=MessageType.TEXT,
        server_default=MessageType.TEXT,
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=MessageStatus.SENT,
        server_default=MessageStatus.SENT,
        index=True,
    )
    is_edited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ── Relationships ────────────────────────────────────────────────────────
    chat: Mapped["ChatORM"] = relationship("ChatORM", back_populates="messages")
    sender: Mapped["UserORM | None"] = relationship("UserORM", back_populates="sent_messages")
    reply_to: Mapped["MessageORM | None"] = relationship(
        "MessageORM",
        remote_side="MessageORM.id",
        foreign_keys=[reply_to_id],
    )
    read_by: Mapped[list["MessageReadStatusORM"]] = relationship(
        "MessageReadStatusORM",
        back_populates="message",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<MessageORM id={self.id} chat={self.chat_id} "
            f"sender={self.sender_id} type={self.type}>"
        )


class MessageReadStatusORM(Base):
    """
    Per-user read receipt for a message.
    Critical for group chats where each member's read state is independent.
    """

    __tablename__ = "message_read_status"
    __table_args__ = (
        UniqueConstraint("message_id", "user_id", name="uq_message_read"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ── Relationships ────────────────────────────────────────────────────────
    message: Mapped["MessageORM"] = relationship("MessageORM", back_populates="read_by")
    user: Mapped["UserORM"] = relationship("UserORM", back_populates="read_receipts")

    def __repr__(self) -> str:
        return f"<MessageReadStatusORM msg={self.message_id} user={self.user_id}>"