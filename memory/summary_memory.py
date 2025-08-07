from langchain.memory import ConversationSummaryBufferMemory
# from langchain_community.chat_models import GoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import settings

def get_summary_memory():
    summary_llm = ChatGoogleGenerativeAI(temperature=0, model=settings.model_name, google_api_key=settings.google_api_key)
    return ConversationSummaryBufferMemory(
        llm=summary_llm,
        max_token_limit=settings.max_token_limit,
        memory_key="chat_history",
        return_messages=True
    )
