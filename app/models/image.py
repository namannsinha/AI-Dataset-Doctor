from pydantic import BaseModel


class ImageRecord(BaseModel):
    id: str
    path: str
    original_path: str
    filename: str

    label: str | None = None
    split: str | None = None

    width: int | None = None
    height: int | None = None
    format: str | None = None
    file_size: int