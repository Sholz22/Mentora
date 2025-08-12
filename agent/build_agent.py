from memory.summary_memory import get_summary_memory 
from src.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from src.prompts import system_prompt
from tools.career_tools import rag_tool, salary_tool, resume_tool, job_explainer_tool
from tools.profile_tools import update_user_profile_tool, get_user_profile_tool


def build_career_agent():
    llm = ChatGoogleGenerativeAI(
        temperature=settings.temperature,
        model=settings.model_name,
        google_api_key=settings.google_api_key,
        convert_system_message_to_human=True 
    )

    memory = get_summary_memory()

    tools = [
        get_user_profile_tool,
        rag_tool,
        salary_tool,
        resume_tool,
        job_explainer_tool,
        update_user_profile_tool
    ]

    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        agent_kwargs={
            "system_message": system_prompt(),
            "handle_parsing_errors": True 
        },
        max_iterations=5,  
        early_stopping_method="generate"  
    )
