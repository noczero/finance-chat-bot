from fastapi import APIRouter

from routes import chat, document, conversation

api_router = APIRouter()

api_router.include_router(chat.router, tags=["chats"])
api_router.include_router(document.router, tags=["documents"])
api_router.include_router(conversation.router, tags=["conversations"])
