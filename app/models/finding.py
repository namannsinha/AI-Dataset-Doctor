from pydantic import BaseModel


class Finding(BaseModel):
    image_id: str

    issue_type: str
    severity: str

    reason: str

    value: float | None = None
    threshold: float | None = None