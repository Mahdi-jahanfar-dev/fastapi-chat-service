from enum import Enum

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base, TimestampMixin


class ChatType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"


class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class ChatORM(Base, TimestampMixin):
    """
    A conversation — either a private 1-to-1 or a group chat.
    title/description/avatar_url are only meaningful for GROUP chats.
    """

    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ── Relationships ────────────────────────────────────────────────────────
    members: Mapped[list["ChatMemberORM"]] = relationship(
        "ChatMemberORM",
        back_populates="chat",
        lazy="select",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["MessageORM"]] = relationship(
        "MessageORM",
        back_populates="chat",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ChatORM id={self.id} type={self.type} title={self.title!r}>"


class ChatMemberORM(Base, TimestampMixin):
    """
    Join table between ChatORM and UserORM.
    Holds per-member metadata: role and mute preference.
    """

    __tablename__ = "chat_members"
    __table_args__ = (
        UniqueConstraint("chat_id", "user_id", name="uq_chat_member"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=MemberRole.MEMBER,
        server_default=MemberRole.MEMBER,
    )
    is_muted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ── Relationships ────────────────────────────────────────────────────────
    chat: Mapped["ChatORM"] = relationship("ChatORM", back_populates="members")
    user: Mapped["UserORM"] = relationship("UserORM", back_populates="chat_memberships")

    def __repr__(self) -> str:
        return (
            f"<ChatMemberORM chat={self.chat_id} "
            f"user={self.user_id} role={self.role}>"
        )