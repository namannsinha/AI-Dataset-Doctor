from pydantic import BaseModel, Field

from app.models.finding import Finding


class AnalysisResult(BaseModel):
    analyzer: str

    images_checked: int

    findings: list[Finding] = Field(
        default_factory=list
    )

    cluster_assignments: dict[str, int] = Field(
        default_factory=dict
    )

    @property
    def issues_found(self) -> int:
        return len(self.findings)