from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from db import Base
from db.models import VARCHAR, TIMESTAMP


class Conversation(Base):
    __tablename__ = "conversations"

    token: Mapped[str] = mapped_column(String(20), primary_key=True)

    name: Mapped[VARCHAR]
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation"
    )

    created_at: Mapped[TIMESTAMP]
