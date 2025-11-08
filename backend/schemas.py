from pydantic import BaseModel, Field
from typing import List, Optional

class Resume(BaseModel):
    text: Optional[str] = None
    job_title: str
    skills: List[str] = Field(default_factory=list)

class AnalysisResult(BaseModel):
    job_title: str
    checklist: List[str]
    matched_skills: List[str]
    missing_skills: List[str]

