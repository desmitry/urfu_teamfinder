from sqlalchemy import (
    Column, Text, Boolean, Integer, ForeignKey, BigInteger, LargeBinary
)
from src.core.postgres.wrapper import Base
from sqlalchemy.orm import relationship, mapped_column


class Account(Base):
    """Represents user account."""

    type = Column(Text, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    handle = Column(Text, nullable=True)
    full_name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    image = Column(LargeBinary, nullable=True)

    account_tags = relationship(
        "AccountTag", back_populates="account"
    )
    likes = relationship(
        "Like",
        back_populates="liker_account",
        foreign_keys="Like.liker_account_id"
    )
    liked_by = relationship(
        "Like",
        back_populates="liked_account",
        foreign_keys = "Like.liked_account_id"
    )


class Like(Base):
    """Represents user account like."""

    liker_account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    liked_account_id = Column(Integer, ForeignKey("account.id"), nullable=False)

    liker_account = relationship(
        "Account",
        back_populates="likes",
        foreign_keys="Like.liker_account_id",
        uselist=False
    )
    liked_account = relationship(
        "Account",
        back_populates="liked_by",
        foreign_keys="Like.liked_account_id",
        uselist=False
    )


class AccountTag(Base):
    """Represents account-tag relationship."""

    account_id = Column(Integer, ForeignKey("account.id"))
    tag_id = Column(Integer, ForeignKey("tag.id"))

    account = relationship(
        "Account", back_populates="account_tags", uselist=False
    )
    tag = relationship(
        "Tag", back_populates="account_tags", uselist=False
    )


class Tag(Base):
    """Represents tag."""

    title = Column(Text, nullable=False)

    account_tags = relationship(
        "AccountTag", back_populates="tag"
    )
