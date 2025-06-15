from typing import List, Dict, Any, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import os
from dotenv import load_dotenv
from services.vector_store import VectorStoreService
from config import settings
import logging
import time

load_dotenv()

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self, vector_store):
        """Initialize RAG pipeline components"""
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            temperature=0.7
        )
        
        # Initialize prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant that answers questions about financial statements. 
            Use the following context to answer the question. If you don't know the answer, just say that you don't know.
            
            Context: {context}
            
            Question: {question}"""),
        ])
        
        self.chain = (
            {"context": lambda x: [doc for doc, _ in self.vector_store.similarity_search(x)], "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def _retrieve_documents(self, question: str) -> List[Tuple[Document, float]]:
        """Retrieve relevant documents for the question with their similarity scores"""
        try:
            return self.vector_store.similarity_search(question)
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise

    def _generate_context(self, documents: List[Tuple[Document, float]]) -> str:
        """Generate context from retrieved documents"""
        return "\n\n".join([doc.page_content for doc, _ in documents])

    def _generate_llm_response(self, question: str, context: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Generate LLM response using context and chat history"""
        try:
            # Format chat history
            chat_history_str = ""
            if chat_history:
                chat_history_str = "\n".join([
                    f"Human: {msg['question']}\nAssistant: {msg['answer']}"
                    for msg in chat_history
                ])
            
            # Create prompt
            prompt = self.prompt.format_messages(
                context=context,
                question=question
            )
            
            # Generate response
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise

    def generate_answer(self, question: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate answer using RAG pipeline"""
        try:
            start_time = time.time()
            
            # Retrieve relevant documents with scores
            documents_with_scores = self._retrieve_documents(question)
            
            # Generate context
            context = self._generate_context(documents_with_scores)
            
            # Generate answer using LLM
            answer = self._generate_llm_response(question, context, chat_history)
            
            # Prepare sources with actual similarity scores
            sources = [
                {
                    "content": doc.page_content,
                    "page": doc.metadata.get("page", 0),
                    "score": float(score),  # Convert score to float to ensure compatibility
                    "metadata": doc.metadata
                }
                for doc, score in documents_with_scores
            ]
            
            processing_time = time.time() - start_time
            
            return {
                "answer": answer,
                "sources": sources,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise

    def process_query(self, query: str) -> str:
        """Process a query using the RAG pipeline."""
        return self.chain.invoke(query)

    def process_documents(self, documents: List[Document]) -> None:
        """Process and store documents in the vector store."""
        self.vector_store.add_documents(documents) 