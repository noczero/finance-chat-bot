from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config import settings


class ConversationNameGenerator:
    def __init__(self, question: str, answer: str):
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            model=settings.llm_model,
            temperature=0.9,
            max_tokens=20,
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
            Generate concise and relevant conversation name for the given question. 
            Start response with emoji or relevant symbol.
            Here's the answer of the question:
            {answer}""",
                ),
                ("user", f"{question}"),
            ]
        )

    def generate(self):
        prompt = self.prompt.format_messages()
        return self.llm.invoke(prompt).content
