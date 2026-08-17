from pydantic import BaseModel


class ImageEmbedding(BaseModel):

    image_id: str
    label: str | None
    embedding: list[float]