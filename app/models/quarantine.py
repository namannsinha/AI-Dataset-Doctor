from pydantic import BaseModel


class QuarantineRecord(BaseModel):
    image_id: str

    original_path: str
    quarantine_path: str

    reason: str
    analyzer: str