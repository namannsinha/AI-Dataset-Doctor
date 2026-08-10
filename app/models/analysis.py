from pydantic import BaseModel, Field

from app.models.finding import Finding


class AnalysisResult(BaseModel):
    analyzer: str

    images_checked: int

    findings: list[Finding] = Field(default_factory=list)

    @property
    def issues_found(self) -> int:
        return len(self.findings)