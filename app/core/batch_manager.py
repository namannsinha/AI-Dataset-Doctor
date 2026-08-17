from collections.abc import Iterable

from app.models import ImageRecord
from app.models.ImageBatch import ImageBatch


class BatchManager:

    def __init__(
        self,
        images: Iterable[ImageRecord],
        batch_size: int,
    ):
        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than 0"
            )

        self.images = images
        self.batch_size = batch_size

    def __iter__(self):

        batch = []
        batch_id = 1

        for image in self.images:

            batch.append(image)

            if len(batch) == self.batch_size:

                yield ImageBatch(
                    batch_id=batch_id,
                    images=batch,
                )

                batch = []
                batch_id += 1

        if batch:

            yield ImageBatch(
                batch_id=batch_id,
                images=batch,
            )