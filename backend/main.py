from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import database

from routes import api_router

from config import settings
import logging
import os

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG-based Financial Statement Q&A System",
    description="AI-powered Q&A system for financial documents using RAG",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting RAG Q&A System...")
    os.makedirs(settings.pdf_upload_path, exist_ok=True)
    database.setup_db(is_drop_table=False)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RAG-based Financial Statement Q&A System is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug)
