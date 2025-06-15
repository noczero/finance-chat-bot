from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models.schemas import ChatRequest, ChatResponse, DocumentsResponse, UploadResponse, ChunksResponse
from services.pdf_processor import PDFProcessor
from services.vector_store import VectorStore
from services.rag_pipeline import RAGPipeline
from config import settings
import logging
import time
import os
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="RAG-based Financial Statement Q&A System",
    description="AI-powered Q&A system for financial documents using RAG",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_processor = PDFProcessor()
vector_store = VectorStore()
rag_pipeline = RAGPipeline(vector_store)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting RAG Q&A System...")
    # Create upload directory if it doesn't exist
    os.makedirs(settings.pdf_upload_path, exist_ok=True)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RAG-based Financial Statement Q&A System is running"}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file
        file_path = os.path.join(settings.pdf_upload_path, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        start_time = time.time()
        
        # Process PDF
        documents = pdf_processor.process_pdf(file_path)
        
        # Store in vector database
        vector_store.add_documents(documents)
        
        processing_time = time.time() - start_time
        
        return UploadResponse(
            message="PDF processed successfully",
            filename=file.filename,
            chunks_count=len(documents),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Process chat request and return AI response"""
    try:
        # Generate answer using RAG pipeline
        result = rag_pipeline.generate_answer(
            question=request.question,
            chat_history=request.chat_history
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            processing_time=result["processing_time"]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def get_documents():
    """Get list of processed documents"""
    try:
        # Get document information from vector store
        documents = vector_store.get_document_info()
        
        return DocumentsResponse(documents=documents)
        
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chunks")
async def get_chunks(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get document chunks with pagination"""
    try:
        # Get chunks from vector store with pagination
        chunks, total_count = vector_store.get_chunks(limit=limit, offset=offset)
        
        return ChunksResponse(
            chunks=chunks,
            total_count=total_count
        )
        
    except Exception as e:
        logger.error(f"Error getting chunks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/clear")
async def clear_all_data():
    """Clear all data including vector store and uploaded files"""
    try:
        result = vector_store.clear_all(settings.pdf_upload_path)
        return {
            "message": "All data cleared successfully",
            "deleted_files": result["deleted_files"],
            "cleared_chunks": result["cleared_chunks"]
        }
    except Exception as e:
        logger.error(f"Error clearing data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug) 