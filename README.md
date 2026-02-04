# PaperLens

A RAG (Retrieval-Augmented Generation) based application that analyzes research papers (PDFs) and allows users to ask questions about them.

## Features

- **Upload & Process**: Upload PDF research papers.
- **Automated Summarization**: Generates structured notes including Problem Statement, Methodology, and Key Takeaways.
- **Interactive Q&A**: Chat with your document to get specific answers.
- **RAG Pipeline**: Built with LangChain, FAISS, and Hugging Face embeddings.

## Tech Stack

- **Backend**: FastAPI, Python, LangChain, FAISS, Hugging Face
- **Frontend**: React, Vite
- **LLM**: Uses Hugging Face Inference API (Zephyr-7b-beta by default)

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js & npm

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the `backend` directory with your Hugging Face API token:

   ```env
   HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
   ```

5. Run the server:
   ```bash
   python main.py
   ```
   The backend will start on `http://localhost:8000`.

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`.

## Usage

1. Open the frontend in your browser.
2. Upload a PDF file.
3. Click "Generate Structured Analysis" to see the summary.
4. Use the chat interface to ask questions about the paper.

## License

MIT
