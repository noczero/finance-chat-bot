import os
import time

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.logger import logger

from config import settings
from models.schemas import UploadResponse, DocumentsResponse, ChunksResponse
from services.pdf_processor import PDFProcessor
from services.vector_store import VectorStore

router = APIRouter()

pdf_processor = PDFProcessor()
vector_store = VectorStore()


@router.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        file_path = os.path.join(settings.pdf_upload_path, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        start_time = time.time()

        documents = pdf_processor.process_pdf(file_path)

        vector_store.add_documents(documents)

        processing_time = time.time() - start_time

        return UploadResponse(
            message="PDF processed successfully",
            filename=file.filename,
            chunks_count=len(documents),
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/documents")
async def get_documents():
    """Get list of processed documents"""
    try:
        documents = vector_store.get_document_info()

        return DocumentsResponse(documents=documents)

    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/documents/chunks")
async def get_chunks(
    limit: int = Query(default=100, ge=1, le=1000), offset: int = Query(default=0, ge=0)
):
    """Get document chunks with pagination"""
    try:
        chunks, total_count = vector_store.get_chunks(limit=limit, offset=offset)

        return ChunksResponse(chunks=chunks, total_count=total_count)

    except Exception as e:
        logger.error(f"Error getting chunks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/documents")
async def clear_all_documents():
    """Clear all data including vector store and uploaded files"""
    try:
        result = vector_store.clear_all(settings.pdf_upload_path)
        return {
            "message": "All data cleared successfully",
            "deleted_files": result["deleted_files"],
            "cleared_chunks": result["cleared_chunks"],
        }
    except Exception as e:
        logger.error(f"Error clearing data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
