from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from analyzer import analyze_full

app = FastAPI(title="AI Resume Analyzer API")


class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description: str


class AnalyzeResponse(BaseModel):
    scores: dict
    interview_qa: dict
    rewrites: dict
    report: dict


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyse", response_model=AnalyzeResponse)
def analyse(request: AnalyzeRequest):
    if not request.resume_text.strip():
        raise HTTPException(status_code=422, detail="Resume text cannot be empty")
    if not request.job_description.strip():
        raise HTTPException(status_code=422, detail="Job description cannot be empty")
    if len(request.job_description) > 5000:
        raise HTTPException(status_code=422, detail="Job description exceeds 5000 characters")

    try:
        result = analyze_full(request.resume_text, request.job_description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")