from langchain.tools import Tool
from src.config import settings
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.schema.document import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Personality Tool
def personality_tool_fn(query: str) -> str:
    return f"Based on your input, here's a personality insight: '{query}'"

personality_tool = Tool.from_function(
    func=personality_tool_fn,
    name="PersonalityProfiler",
    description="Analyzes user personality traits, interests, and preferences to recommend suitable careers."
)


# Skills Tool
def skills_tool_fn(query: str) -> str:
    return f"Skill analysis result: '{query}'"

skills_tool = Tool.from_function(
    func=skills_tool_fn,
    name="SkillEvaluator",
    description="Identifies user's core skills and suggests careers where these skills are valuable."
)


# Job Market Tool
def job_market_tool_fn(query: str) -> str:
    return f"Job market trends: '{query}'"

job_market_tool = Tool.from_function(
    func=job_market_tool_fn,
    name="JobMarketAnalyzer",
    description="Gives job market demand, emerging industries, and location-based opportunities."
)

# Education Path Tool
def education_path_tool_fn(query: str) -> str:
    return f"Suggested learning path: '{query}'"

education_path_tool = Tool.from_function(
    func=education_path_tool_fn,
    name="EducationAdvisor",
    description="Recommends degrees, courses, or certifications based on user's goals."
)

# Career Switch Tool
def switch_tool_fn(query: str) -> str:
    return f"Career switch advice: '{query}'"

switch_tool = Tool.from_function(
    func=switch_tool_fn,
    name="CareerSwitchAdvisor",
    description="Provides personalized advice for users looking to transition into new industries."
)

# Career Roadmap Tool
def roadmap_tool_fn(query: str) -> str:
    return f"Career roadmap: '{query}'"

roadmap_tool = Tool.from_function(
    func=roadmap_tool_fn,
    name="CareerPathPlanner",
    description="Maps out a step-by-step path from current state to desired career goal."
)

# Virtual Mentor Tool
def mentor_tool_fn(query: str) -> str:
    return f"Mentor advice: '{query}'"

mentor_tool = Tool.from_function(
    func=mentor_tool_fn,
    name="VirtualMentor",
    description="Gives motivational or practical advice from the perspective of a mentor in the chosen field."
)

# Salary Benchmark Tool
def salary_tool_fn(query: str) -> str:
    return f"Salary information: '{query}'"

salary_tool = Tool.from_function(
    func=salary_tool_fn,
    name="SalaryBenchmark",
    description="Provides average salaries by job role, experience level, and region."
)

# Resume Reviewer Tool
def resume_tool_fn(query: str) -> str:
    return f"Resume feedback: '{query}'"

resume_tool = Tool.from_function(
    func=resume_tool_fn,
    name="ResumeReviewer",
    description="Gives constructive feedback on user's resume or portfolio based on target career."
)

# Job Explainer Tool
def job_explainer_tool_fn(query: str) -> str:
    return f"Job explanation: '{query}'"

job_explainer_tool = Tool.from_function(
    func=job_explainer_tool_fn,
    name="JobExplainer",
    description="Explains what a specific job title involves, daily tasks, and long-term growth."
)

# Document Search Tool (RAG) using Gemini
text_loader = TextLoader("data/career_guides.txt")
pdf_loader = PyMuPDFLoader("data/career_reports.pdf")
career_docs = text_loader.load() + pdf_loader.load()

if career_docs:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.google_api_key)
    vectorstore = FAISS.from_documents(career_docs, embeddings)
    qa_chain = RetrievalQA.from_chain_type(llm=ChatGoogleGenerativeAI(model=settings.model_name, temperature=0, google_api_key=settings.google_api_key),
                                           retriever=vectorstore.as_retriever(),
                                           return_source_documents=True)

    rag_tool = Tool.from_function(
        func=lambda q: qa_chain.invoke(q),
        name="CareerDocSearcher",
        description="Searches government career guides, HR reports, and industry docs to give informed answers."
    )
else:
    rag_tool = Tool.from_function(
        func=lambda _: "No career documents available right now.",
        name="CareerDocSearcher",
        description="(Temporarily disabled — no career documents found.)"
    )


































# # Document Search Tool (RAG) using Gemini
# from langchain_community.vectorstores import FAISS
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain.chains import RetrievalQA
# from langchain_community.document_loaders import TextLoader, PyMuPDFLoader #WebBaseLoader
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.schema.document import Document

# # Load from text file(s)
# text_loader = TextLoader("data/agriculture_docs.txt")
# text_docs = text_loader.load()

# # Load from PDF
# pdf_loader = PyMuPDFLoader("data/farming_manual.pdf")
# pdf_docs = pdf_loader.load()

# # Combine all documents
# all_docs: list[Document] = text_docs + pdf_docs

# if all_docs:
#     rag_llm = ChatGoogleGenerativeAI(model=settings.model_name, temperature=0, google_api_key=settings.google_api_key)

#     def get_google_embeddings():
#         from langchain_google_genai import GoogleGenerativeAIEmbeddings
#         from src.config import settings
#         return GoogleGenerativeAIEmbeddings(
#             model="models/embedding-001",
#             google_api_key=settings.google_api_key
#         )
#     embedding = get_google_embeddings()

#     # Vector store
#     vectorstore = FAISS.from_documents(all_docs, embedding)

#     # RAG QA chain
#     qa_chain = RetrievalQA.from_chain_type(
#         llm=rag_llm,
#         retriever=vectorstore.as_retriever(),
#         return_source_documents=True
#     )

#     # RAG tool wrapper
#     rag_tool = Tool.from_function(
#         func=lambda q: qa_chain.run(q),
#         name="DocSearcher",
#         description="Looks up government docs, PDF manuals, and agricultural reports to give evidence-based answers."
#     )

# else:
#     rag_tool = Tool.from_function(
#         func=lambda _: "No documents available at the moment.",
#         name="DocSearcher",
#         description="(Temporarily disabled — no documents found.)"
#     )



# Load from websites
# web_loader = WebBaseLoader(["https://example-agriculture.com/tips", "https://gov.ng/farming-guidelines"])
# web_docs = web_loader.load()