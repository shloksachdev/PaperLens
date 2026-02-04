import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Global storage for vector stores (in memory for simplicity)
vector_stores = {}

def process_pdf(file_path: str) -> str:
    doc_id = os.path.basename(file_path)
    
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    if not texts:
        print(f"Warning: No texts found for {doc_id}. Using placeholder.")
        from langchain.schema import Document
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
    
    # We will ask specific questions to populate the structure
    # A single prompt could work, but chaining specific queries might be more robust.
    # For speed, let's try a comprehensive single system prompt or a few key queries.
    
    # Let's do a structured prompt approach.
    sections = [
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
    
    notes = {}
    
    # We can try to get everything in one go to save API calls, but context window might be an issue.
    # Let's try grouping them.
    
    prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")

    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    # Group 1: Introduction
    query_intro = "Summarize the Problem Statement and Motivation of this paper. Return the answer as a concise list of bullet points."
    response = retrieval_chain.invoke({"input": query_intro})
    notes["Introduction"] = response["answer"]
    
    # Group 2: Key Concepts
    query_inov = "What are the Core Innovations and Key Contributions of this paper? Return the answer as a concise list of bullet points."
    response = retrieval_chain.invoke({"input": query_inov})
    notes["Key Innovations"] = response["answer"]

    # Group 3: Methods
    query_method = "Describe the Methodology, Model Architecture, and Dataset used. Return the answer as a concise list of bullet points."
    response = retrieval_chain.invoke({"input": query_method})
    notes["Methodology"] = response["answer"]
    
    # Group 4: Results
    query_results = "Summarize the Experiments, Results, and Key Takeaways. Return the answer as a concise list of bullet points."
    response = retrieval_chain.invoke({"input": query_results})
    notes["Results"] = response["answer"]
    
    # Group 5: Conclusion
    query_conc = "What are the Limitations, Future Work, and Practical Applications stated? Return the answer as a concise list of bullet points."
    response = retrieval_chain.invoke({"input": query_conc})
    notes["Conclusion"] = response["answer"]

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

    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    response = retrieval_chain.invoke({"input": query})
    return response["answer"]
