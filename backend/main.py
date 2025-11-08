from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from PyPDF2 import PdfReader
from database import create_document, get_documents
from schemas import Resume, AnalysisResult

app = FastAPI(title="Resume Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple skill dictionary per job title for demo purposes
JOB_SKILLS: Dict[str, List[str]] = {
    "software engineer": [
        "python", "javascript", "react", "node", "git", "docker", "testing", "sql", "algorithms", "data structures"
    ],
    "data scientist": [
        "python", "pandas", "numpy", "scikit-learn", "statistics", "machine learning", "sql", "matplotlib", "deep learning"
    ],
    "product manager": [
        "roadmapping", "stakeholder management", "analytics", "user research", "a/b testing", "agile", "communication"
    ],
}


def extract_text_from_pdf(file: UploadFile) -> str:
    reader = PdfReader(file.file)
    text = []
    for page in reader.pages:
        text.append(page.extract_text() or "")
    return "\n".join(text)


def analyze_resume_text(text: str, job_title: str) -> AnalysisResult:
    jt = job_title.strip().lower()
    required = JOB_SKILLS.get(jt, [])
    words = set(w.strip(".,;:()[]{}!?").lower() for w in text.split())
    matched = [s for s in required if s in words]
    missing = [s for s in required if s not in words]

    checklist: List[str] = []
    if required:
        checklist.append(f"Customize summary to emphasize {jt} focus")
        checklist.append("Quantify 3-5 achievements with metrics (% or $)")
        checklist.append("Highlight top 5 relevant skills in first third of page")
        if missing:
            checklist.append("Add or expand on: " + ", ".join(missing))
        checklist.append("Ensure ATS-friendly formatting (simple headings, no tables)")
        checklist.append("Include links to portfolio/GitHub/LinkedIn where relevant")
    else:
        checklist.append("Provide a clear job title to tailor suggestions")

    return AnalysisResult(
        job_title=jt,
        checklist=checklist,
        matched_skills=matched,
        missing_skills=missing,
    )


@app.post("/analyze/text", response_model=AnalysisResult)
async def analyze_text_endpoint(payload: Resume):
    result = analyze_resume_text(payload.text or "", payload.job_title)
    create_document("analysis", {
        "job_title": result.job_title,
        "matched_skills": result.matched_skills,
        "missing_skills": result.missing_skills,
        "checklist": result.checklist,
        "source": "text",
    })
    return result


@app.post("/analyze/upload", response_model=AnalysisResult)
async def analyze_upload_endpoint(
    job_title: str = Form(...),
    file: UploadFile = File(...)
):
    content = ""
    if file.content_type == "application/pdf":
        content = extract_text_from_pdf(file)
    else:
        content = (await file.read()).decode("utf-8", errors="ignore")
    result = analyze_resume_text(content, job_title)
    create_document("analysis", {
        "job_title": result.job_title,
        "matched_skills": result.matched_skills,
        "missing_skills": result.missing_skills,
        "checklist": result.checklist,
        "source": "upload",
        "filename": file.filename,
    })
    return result


@app.get("/history")
async def history(limit: int = 20):
    return get_documents("analysis", {}, limit)


@app.get("/test")
async def test():
    return {"status": "ok"}
