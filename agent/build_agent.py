from memory.summary_memory import get_summary_memory 
from src.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from src.prompts import system_prompt
from tools.tools import rag_tool, personality_tool, skills_tool, job_market_tool, education_path_tool, switch_tool, roadmap_tool, mentor_tool, salary_tool, resume_tool, job_explainer_tool


def build_career_agent():
    llm = ChatGoogleGenerativeAI(
        temperature=settings.temperature,
        model=settings.model_name,
        google_api_key=settings.google_api_key,
        convert_system_message_to_human=True 
    )

    memory = get_summary_memory()

    tools = [
        personality_tool,
        skills_tool,
        job_market_tool,
        education_path_tool,
        switch_tool,
        roadmap_tool,
        mentor_tool,
        rag_tool,
        salary_tool,
        resume_tool,
        job_explainer_tool
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
