from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
import os
from rag_pipeline import process_pdf, generate_notes, answer_query

app = FastAPI(title="PaperLens API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "PaperLens API is running"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the PDF immediately upon upload
        doc_id = process_pdf(file_path)
        return {"filename": file.filename, "doc_id": doc_id, "message": "File processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/{doc_id}")
async def analyze_pdf(doc_id: str):
    try:
        notes = generate_notes(doc_id)
        return notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/{doc_id}")
async def ask_question(doc_id: str, query: str):
    try:
        answer = answer_query(doc_id, query)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
