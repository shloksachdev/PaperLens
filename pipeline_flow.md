# PaperLens Pipeline Flows

Here is an architectural visualization of how your currently existing pipeline in `rag_pipeline.py` works. This follows a "Flowise-like" node architecture where different LangChain components interact with one another.

No changes have been made to your project's code.

---

## 1. Document Ingestion Pipeline

When you upload a PDF (calling `process_pdf`), the document passes through a series of steps to be chunked and indexed into the local FAISS vector store.

```mermaid
graph LR
    classDef node fill:#f9f9f9,stroke:#333,stroke-width:2px,color:#222,rx:5px,ry:5px;
    classDef model fill:#e8f4f8,stroke:#333,stroke-width:2px,color:#222,rx:5px,ry:5px;
    classDef store fill:#f3e8f8,stroke:#333,stroke-width:2px,color:#222,rx:5px,ry:5px;

    File(("📄 PDF File Input"))
    
    subgraph Ingestion flow
        Loader["📄 PyPDFLoader"]:::node
        Splitter["✂️ RecursiveCharacterTextSplitter<br/>(chunk=1000, overlap=200)"]:::node
        Emb["🧠 HuggingFaceEmbeddings<br/>(all-MiniLM-L6-v2)"]:::model
        VS["🗄️ FAISS<br/>(Vector Store)"]:::store
    end
    
    File --> Loader
    Loader -->|List of Documents| Splitter
    Splitter -->|Chunked Texts| VS
    Emb -->|Generates Embeddings| VS
    VS -.->|Stores vectors in memory| Storage[("vector_stores[doc_id]")]
```

---

## 2. Runtime & Generation Pipeline

When you ask a question or request structured analysis (calling `answer_query` or `generate_notes`), the system retrieves the respective vector store, pulls the relevant context, and passes it through an LCEL (LangChain Expression Language) chain to the language model.

```mermaid
graph TD
    classDef node fill:#f9f9f9,stroke:#333,stroke-width:2px,color:#222,rx:5px,ry:5px;
    classDef model fill:#e8f4f8,stroke:#333,stroke-width:2px,color:#222,rx:5px,ry:5px;
    classDef store fill:#f3e8f8,stroke:#333,stroke-width:2px,color:#222,rx:5px,ry:5px;
    classDef inout fill:#fff5e6,stroke:#f5a623,stroke-width:2px,color:#222,rx:5px,ry:5px;

    Input(("👤 Query Input")):::inout
    Response(("✅ Final Answer")):::inout
    
    Storage[("vector_stores[doc_id]")]
    
    subgraph Retrieval
        VS["🗄️ FAISS"]:::store
        Retriever["🔍 Retriever<br/>(k=5 for notes, k=3 for Q&A)"]:::node
        Format["📝 format_docs()<br/>(Joins with double newlines)"]:::node
    end
    
    subgraph LCEL Pipeline
        Passthrough["⚙️ RunnablePassthrough<br/>Assigns {context} and {input}"]:::node
        Prompt["💬 ChatPromptTemplate<br/>Injects into XML-like prompt"]:::node
        LLM["🤖 CustomHuggingFaceLLM<br/>(zephyr-7b-beta)"]:::model
        Parser["📤 StrOutputParser"]:::node
    end

    Storage -.-> VS
    VS --> Retriever
    Input --> Passthrough
    Input --> Retriever
    
    Retriever -->|Relevant Docs| Format
    Format -->|Context String| Passthrough
    
    Passthrough -->|Dict context+input| Prompt
    Prompt -->|Formatted String| LLM
    LLM -->|Raw LLM Output| Parser
    Parser --> Response
```

### Key Differences in your logic:
* **Generation**: During generation (`generate_notes`), it iterates over a predefined list of sections (like "Methodology", "Dataset") and runs this pipeline individually for every section.
* **Retrieval (`k` size)**: It pulls `k=5` snippets to extract more detailed content for notes, while finding quicker context (`k=3`) for direct query answering.
