import uuid

from fastapi import Depends, APIRouter, HTTPException
from fastapi.logger import logger

from db import Conversation, Message
from db.session import get_session
from models.schemas import ChatRequest, MessageSchema, ChatResponse
from services.conversation_name_generator import ConversationNameGenerator
from services.rag_pipeline import RAGPipeline
from services.vector_store import VectorStore

router = APIRouter()

vector_store = VectorStore()
rag_pipeline = RAGPipeline(vector_store)


@router.post("/api/chat")
async def chat(request: ChatRequest, Session=Depends(get_session)):
    """Process chat request and return AI response"""
    try:
        with Session as session:
            conversation_token = request.conversation_token or str(uuid.uuid4())
            conversation = (
                session.query(Conversation).filter_by(token=conversation_token).first()
            )

            chat_history = []
            if conversation:
                chat_history = [
                    MessageSchema.from_orm(message) for message in conversation.messages
                ]

            result = rag_pipeline.generate_answer(
                question=request.question,
                chat_history=chat_history,
            )

            if not conversation:
                name = ConversationNameGenerator(
                    request.question, result["answer"]
                ).generate()
                conversation = Conversation(name=name, token=conversation_token)
                session.add(conversation)
                session.commit()

            user_message = Message(
                conversation=conversation, role="user", content=request.question
            )
            assistant_message = Message(
                conversation=conversation, role="assistant", content=result["answer"]
            )
            session.add_all([user_message, assistant_message])
            session.commit()

            return ChatResponse(
                answer=result["answer"],
                sources=result["sources"],
                processing_time=result["processing_time"],
                conversation_token=conversation_token,
                created_at=assistant_message.created_at,
            )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
