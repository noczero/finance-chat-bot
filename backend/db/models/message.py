from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from db.models import BaseModel, VARCHAR


class Message(BaseModel):
    __tablename__ = "messages"

    conversation_token: Mapped[str] = mapped_column(ForeignKey("conversations.token"))
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    role: Mapped[VARCHAR]
    content: Mapped[Text] = mapped_column(Text, nullable=False)
