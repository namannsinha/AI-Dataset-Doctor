from pydantic import BaseModel, Field

from app.models import DatasetType


class DatasetMetadata(BaseModel):
    dataset_type: DatasetType

    classes: list[str] = Field(
        default_factory=list
    )

    splits: list[str] = Field(
        default_factory=list
    )

    image_count: int = 0