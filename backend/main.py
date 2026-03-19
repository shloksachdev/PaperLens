from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
import os
from fastapi import Depends
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models
from auth import verify_password, get_password_hash, create_access_token
from rag_pipeline import process_pdf, generate_notes, answer_query

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

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

from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str = None

class LoginRequest(BaseModel):
    username: str
    password: str

class GoogleLoginRequest(BaseModel):
    credential: str

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID_HERE")

@app.post("/register")
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == req.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(req.password)
    new_user = models.User(email=req.email, hashed_password=hashed_pw, full_name=req.full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == req.username).first()
    if not db_user or not db_user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(req.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.email})
    return {"success": True, "token": access_token, "user": db_user.email}

@app.post("/auth/google")
async def google_login(req: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            req.credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )
        email = idinfo.get("email")
        name = idinfo.get("name")
        
        # Check if user exists
        db_user = db.query(models.User).filter(models.User.email == email).first()
        if not db_user:
            # Create a new user for Google OAuth
            db_user = models.User(email=email, full_name=name)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
        access_token = create_access_token(data={"sub": email})
        return {"success": True, "token": access_token, "user": email}
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
