from pydantic import BaseModel


class ImageHash(BaseModel):
    image_id: str
    file_hash: str