from typing import List, Optional, Tuple, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
import logging
import chromadb
from chromadb.config import Settings as ChromaSettings
from datetime import datetime
import uuid
import shutil

logger = logging.getLogger(__name__)

load_dotenv()

class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-ada-002"
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        self.vector_store = Chroma(
            persist_directory=os.getenv("VECTOR_DB_PATH", "data/vector_store"),
            embedding_function=self.embeddings
        )

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        texts = self.text_splitter.split_documents(documents)
        self.vector_store.add_documents(texts)
        # The vector store automatically persists when using persist_directory

    def similarity_search(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Search for similar documents with their similarity scores."""
        return self.vector_store.similarity_search_with_score(query, k=k)

    def clear(self) -> None:
        """Clear all documents from the vector store."""
        self.vector_store.delete_collection()
        self.vector_store = Chroma(
            persist_directory=os.getenv("VECTOR_DB_PATH", "data/vector_store"),
            embedding_function=self.embeddings
        )

    def clear_all(self, upload_path: str) -> Dict[str, int]:
        """Clear both vector store and uploaded files."""
        try:
            # Clear vector store
            self.clear()
            
            # Clear uploaded files
            deleted_files = 0
            if os.path.exists(upload_path):
                for filename in os.listdir(upload_path):
                    file_path = os.path.join(upload_path, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            deleted_files += 1
                    except Exception as e:
                        logger.error(f"Error deleting file {file_path}: {str(e)}")
            
            return {
                "deleted_files": deleted_files,
                "cleared_chunks": True
            }
            
        except Exception as e:
            logger.error(f"Error clearing all data: {str(e)}")
            raise

    def get_document_info(self) -> List[Dict]:
        """Get information about all documents in the vector store."""
        try:
            # Get all documents from the collection
            collection = self.vector_store._collection
            results = collection.get()
            
            if not results or not results['metadatas']:
                return []
            
            # Group chunks by source file
            documents = {}
            for metadata in results['metadatas']:
                source = metadata.get('source', 'unknown')
                if source not in documents:
                    documents[source] = {
                        'filename': source,
                        'upload_date': datetime.now().isoformat(),  # You might want to store this in metadata
                        'chunks_count': 0,
                        'status': 'processed'
                    }
                documents[source]['chunks_count'] += 1
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            raise

    def get_chunks(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict], int]:
        """Get chunks with their text and metadata."""
        try:
            # Get all documents from the collection
            collection = self.vector_store._collection
            results = collection.get()
            
            if not results or not results['metadatas'] or not results['documents']:
                return [], 0
            
            # Create chunks with unique IDs
            chunks = []
            for i, (metadata, content) in enumerate(zip(results['metadatas'], results['documents'])):
                if i < offset:
                    continue
                if i >= offset + limit:
                    break
                    
                chunk = {
                    'id': str(uuid.uuid4()),
                    'content': content,
                    'page': metadata.get('page', 0),
                    'metadata': {
                        'source': metadata.get('source', 'unknown'),
                        'page': metadata.get('page', 0)
                    }
                }
                chunks.append(chunk)
            
            total_count = len(results['documents'])
            return chunks, total_count
            
        except Exception as e:
            logger.error(f"Error getting chunks: {str(e)}")
            raise

class VectorStoreService:
    def __init__(self):
        """Initialize vector store with ChromaDB and OpenAI embeddings"""
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-ada-002"
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=os.getenv("VECTOR_DB_PATH", "data/vector_store"),
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        
        # Initialize vector store
        self.vector_store = Chroma(
            client=self.client,
            embedding_function=self.embeddings,
            collection_name="financial_documents"
        )
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store"""
        try:
            self.vector_store.add_documents(documents)
            logger.info(f"Successfully added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """Search for similar documents"""
        try:
            k = k or 4
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            raise
    
    def delete_documents(self, document_ids: List[str]) -> None:
        """Delete documents from vector store"""
        try:
            self.vector_store.delete(document_ids)
            logger.info(f"Successfully deleted {len(document_ids)} documents from vector store")
        except Exception as e:
            logger.error(f"Error deleting documents from vector store: {str(e)}")
            raise
    
    def get_document_count(self) -> int:
        """Get total number of documents in vector store"""
        try:
            return self.vector_store._collection.count()
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            raise 
        # TODO: Return document count
        pass 