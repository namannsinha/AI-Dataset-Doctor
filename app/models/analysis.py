from pydantic import BaseModel, Field

from app.models.finding import Finding


class AnalysisResult(BaseModel):
    analyzer: str

    total_checked: int
    total_flagged: int

    findings: list[Finding] = Field(default_factory=list)

    summary: str