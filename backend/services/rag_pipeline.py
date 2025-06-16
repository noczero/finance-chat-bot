from typing import List, Dict, Any, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import Document, HumanMessage, AIMessage, BaseMessage
from dotenv import load_dotenv

from models.schemas import MessageSchema
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
            openai_api_key=settings.openai_api_key,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.max_tokens,
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are an AI assistant that specializes in summarizing financial statements. 
                                
                    Your task is to provide a clear and concise summary in response to the user's question, based only on the `<context>`.
                    
                    <instructions>
                    1. Base your answer entirely on the provided context. Do not add information or make assumptions.
                    2. Synthesize information from across the document to provide a comprehensive overview of the requested topic (e.g., a policy, a committee's function, or a specific event).
                    3. Use bullet points to structure your answer for clarity where appropriate.
                    4. At the end of your summary, provide a list of all source numbers used in the format: `References:`.
                    5. In <context>, each document consists of a page number, chunk content, and followed by metadata. Split by double newline separator.
                    </instructions>
                    
                    <context>
                    {context}
                    </context>
                    """.strip(),
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{question}"),
            ]
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
        context_parts = []
        for doc, _ in documents:
            page_content = doc.page_content
            metadata = doc.metadata
            page = metadata.get("page", 0)

            formatted_content = (
                f"Page {page}:\n{page_content}\nMetadata: {metadata}".strip()
            )
            context_parts.append(formatted_content)

        return "\n\n".join(context_parts)

    def _generate_llm_response(
        self, question: str, context: str, chat_history: List[MessageSchema] = None
    ) -> str:
        """Generate LLM response using context and chat history"""
        try:

            formatted_chat_history = self._build_chat_history(chat_history)

            prompt = self.prompt.format_messages(
                context=context, question=question, chat_history=formatted_chat_history
            )

            response = self.llm.invoke(prompt)

            return response.content
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise

    def generate_answer(
        self, question: str, chat_history: List[MessageSchema] = None
    ) -> Dict[str, Any]:
        """Generate answer using RAG pipeline"""
        try:
            start_time = time.time()

            documents_with_scores = self._retrieve_documents(question)

            context = self._generate_context(documents_with_scores)

            answer = self._generate_llm_response(question, context, chat_history)

            sources = [
                {
                    "content": doc.page_content,
                    "page": doc.metadata.get("page", 0),
                    "score": float(score),
                    "metadata": doc.metadata,
                }
                for doc, score in documents_with_scores
            ]

            processing_time = time.time() - start_time

            return {
                "answer": answer,
                "sources": sources,
                "processing_time": processing_time,
            }

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise

    def _build_chat_history(
        self, chat_history: List[MessageSchema]
    ) -> List[BaseMessage]:
        """Convert the list of MessageSchema to a list of LangChain Message objects"""
        converted_history = []
        for message in chat_history:
            role = message.role
            content = message.content
            if role == "user":
                converted_history.append(HumanMessage(content=content))
            elif role == "assistant":
                converted_history.append(AIMessage(content=content))
        return converted_history
