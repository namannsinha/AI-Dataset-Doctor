from app.models.image import ImageRecord


class ImageBatch:

    def __init__(
        self,
        batch_id: int,
        images: list[ImageRecord],
    ):
        self.batch_id = batch_id
        self.images = images

    @property
    def size(self) -> int:
        return len(self.images)

    @property
    def total_images(self) -> int:
        return len(self.images)