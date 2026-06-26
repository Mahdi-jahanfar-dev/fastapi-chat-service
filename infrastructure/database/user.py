from enum import Enum

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base, TimestampMixin


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class ContactStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class UserORM(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=UserStatus.ACTIVE,
        server_default=UserStatus.ACTIVE,
    )
    is_online: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ── Relationships ────────────────────────────────────────────────────────
    contacts: Mapped[list["ContactORM"]] = relationship(
        "ContactORM",
        foreign_keys="ContactORM.owner_id",
        back_populates="owner",
        lazy="select",
    )
    chat_memberships: Mapped[list["ChatMemberORM"]] = relationship(
        "ChatMemberORM",
        back_populates="user",
        lazy="select",
    )
    sent_messages: Mapped[list["MessageORM"]] = relationship(
        "MessageORM",
        back_populates="sender",
        lazy="select",
    )
    read_receipts: Mapped[list["MessageReadStatusORM"]] = relationship(
        "MessageReadStatusORM",
        back_populates="user",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<UserORM id={self.id} username={self.username!r}>"


class ContactORM(Base, TimestampMixin):
    """
    Self-referential many-to-many between users.
    owner  → user who added the contact
    contact → user who was added
    """

    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint("owner_id", "contact_id", name="uq_contact_pair"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ContactStatus.PENDING,
        server_default=ContactStatus.PENDING,
    )
    nickname: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # ── Relationships ────────────────────────────────────────────────────────
    owner: Mapped["UserORM"] = relationship(
        "UserORM",
        foreign_keys=[owner_id],
        back_populates="contacts",
    )
    contact: Mapped["UserORM"] = relationship(
        "UserORM",
        foreign_keys=[contact_id],
    )

    def __repr__(self) -> str:
        return (
            f"<ContactORM owner={self.owner_id} "
            f"contact={self.contact_id} status={self.status}>"
        )