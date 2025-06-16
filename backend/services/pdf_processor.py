import os
from typing import List, Dict, Any
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import settings
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self):
        """Initialize text splitter with chunk size and overlap settings"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF and return page-wise content"""
        try:
            pages_content = []
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        pages_content.append(
                            {
                                "page_number": page_num,
                                "content": text,
                                "metadata": {
                                    "source": os.path.basename(file_path),
                                    "page": page_num,
                                },
                            }
                        )
            return pages_content
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def split_into_chunks(self, pages_content: List[Dict[str, Any]]) -> List[Document]:
        """Split page content into chunks"""
        try:
            documents = []
            for page in pages_content:
                chunks = self.text_splitter.split_text(page["content"])
                for chunk in chunks:
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            "source": page["metadata"]["source"],
                            "page": page["metadata"]["page"],
                        },
                    )
                    documents.append(doc)
            return documents
        except Exception as e:
            logger.error(f"Error splitting text into chunks: {str(e)}")
            raise

    def process_pdf(self, file_path: str) -> List[Document]:
        """Process PDF file and return list of Document objects"""
        try:
            # Extract text from PDF
            pages_content = self.extract_text_from_pdf(file_path)

            # Split text into chunks
            documents = self.split_into_chunks(pages_content)

            logger.debug(f"Successfully processed PDF: {file_path}")
            logger.debug(
                f"Generated {len(documents)} chunks from {len(pages_content)} pages"
            )

            return documents
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
