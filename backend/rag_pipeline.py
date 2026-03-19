import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Global storage for vector stores (in memory for simplicity)
vector_stores = {}

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def process_pdf(file_path: str) -> str:
    doc_id = os.path.basename(file_path)
    
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    if not texts:
        print(f"Warning: No texts found for {doc_id}. Using placeholder.")
        from langchain_core.documents import Document
        texts = [Document(page_content="No text content found in this document.", metadata={"source": file_path})]

    # Use a lightweight embedding model
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create vector store
    db = FAISS.from_documents(texts, embeddings)
    vector_stores[doc_id] = db
    
    return doc_id

from custom_llm import CustomHuggingFaceLLM

def get_llm():
    """
    Returns a Custom Hugging Face LLM.
    """
    repo_id = "HuggingFaceH4/zephyr-7b-beta"
    
    # We verify token for clarity but custom_llm handles it too
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not api_token:
        raise ValueError("HUGGINGFACEHUB_API_TOKEN is not set")

    llm = CustomHuggingFaceLLM(repo_id=repo_id, temperature=0.1)
    return llm

def generate_notes(doc_id: str) -> dict:
    """
    Generates structured notes for the given document.
    """
    if doc_id not in vector_stores:
        raise ValueError("Document not found. Please upload it first.")
    
    db = vector_stores[doc_id]
    llm = get_llm()
    retriever = db.as_retriever(search_kwargs={"k": 5}) # Retrieve more context for summarization
    
    notes = {}
    prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")

    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    sections_to_extract = [
        "Problem Statement",
        "Motivation",
        "Methodology",
        "Model / Algorithm",
        "Dataset",
        "Experiments & Results",
        "Limitations",
        "Future Work",
        "Key Takeaways"
    ]
    
    for section in sections_to_extract:
        query = f"Extract and summarize the '{section}' from this document. Provide the answer clearly as a concise list of bullet points."
        notes[section] = rag_chain.invoke(query)

    return notes

def answer_query(doc_id: str, query: str) -> str:
    """
    Answers a specific question based on the document.
    """
    if doc_id not in vector_stores:
        raise ValueError("Document not found. Please upload it first.")
    
    db = vector_stores[doc_id]
    llm = get_llm()
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")

    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(query)
