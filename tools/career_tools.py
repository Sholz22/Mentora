from langchain.tools import Tool
from src.config import settings
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.schema.document import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

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