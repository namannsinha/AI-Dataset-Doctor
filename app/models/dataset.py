from pydantic import BaseModel, Field

from app.models.dataset_type import DatasetType
from app.models.image import ImageRecord


class Dataset(BaseModel):
    dataset_id: str
    name: str

    dataset_type: DatasetType
    source_format: str
    root_path: str

    images: list[ImageRecord] = Field(default_factory=list)

    classes: list[str] = Field(default_factory=list)
    splits: list[str] = Field(default_factory=list)