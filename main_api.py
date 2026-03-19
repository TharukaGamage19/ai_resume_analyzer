from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from analyzer import analyze_full

app = FastAPI()

class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyse")
def analyse(request: AnalyzeRequest):
    if not request.resume_text.strip():
        raise HTTPException(status_code=422, detail="Resume text cannot be empty")
    if not request.job_description.strip():
        raise HTTPException(status_code=422, detail="Job description cannot be empty")
    try:
        return analyze_full(request.resume_text, request.job_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))