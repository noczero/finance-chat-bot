from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc

from db import Conversation
from db.session import get_session
from models.schemas import ConversationSchema, MessageSchema, MessagesResponse

router = APIRouter()


@router.get("/api/conversations")
async def get_conversations(Session=Depends(get_session)):
    """Get list of conversations"""
    with Session as session:
        conversations = (
            session.query(Conversation).order_by(desc(Conversation.created_at)).all()
        )

        if not conversations:
            raise HTTPException(status_code=404, detail="Conversations empty!")

        conversations_data = [
            ConversationSchema.from_orm(conversation) for conversation in conversations
        ]
        return conversations_data


@router.get("/api/conversations/{token}/messages")
async def get_messages(token, Session=Depends(get_session)):
    """Get list of conversations"""
    with Session as session:
        conversation = session.query(Conversation).filter_by(token=token).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found!")

        messages = [
            MessageSchema.from_orm(message) for message in conversation.messages
        ]

        return MessagesResponse(messages=messages)
