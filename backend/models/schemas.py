from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class ChatRequest(BaseModel):
    conversation_token: Optional[str] = ""
    question: str


class DocumentSource(BaseModel):
    content: str
    page: int
    score: float
    metadata: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    answer: str
    sources: List[DocumentSource]
    processing_time: float
    conversation_token: str
    created_at: datetime


class DocumentInfo(BaseModel):
    filename: str
    upload_date: datetime
    chunks_count: int
    status: str


class DocumentsResponse(BaseModel):
    documents: List[DocumentInfo]


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_count: int
    processing_time: float


class ChunkInfo(BaseModel):
    id: str
    content: str
    page: int
    metadata: Dict[str, Any]


class ChunksResponse(BaseModel):
    chunks: List[ChunkInfo]
    total_count: int


class MessageSchema(BaseModel):
    id: int
    conversation_token: str
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class MessagesResponse(BaseModel):
    messages: List[MessageSchema]

    class Config:
        orm_mode = True
        from_attributes = True


class ConversationSchema(BaseModel):
    token: str
    name: str
    messages: List[MessageSchema]  # Assuming MessageSchema is already defined

    class Config:
        orm_mode = True
        from_attributes = True
