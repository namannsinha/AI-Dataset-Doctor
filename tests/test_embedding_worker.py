import numpy as np

from app.core.embedding_worker import EmbeddingWorker
from app.models import ImageEmbedding
from app.models import ImageRecord
from app.models.ImageBatch import ImageBatch


class FakeEmbeddingService:

    def generate_embedding(self, image_path: str):

        if image_path == "image1.jpg":
            return np.array(
                [1.0, 0.0, 0.0]
            )

        return np.array(
            [0.0, 1.0, 0.0]
        )


def test_embedding_worker():

    image1 = ImageRecord(
        id="image1.jpg",
        path="image1.jpg",
        original_path="image1.jpg",
        filename="image1.jpg",
        width=224,
        height=224,
        format="jpg",
        file_size=100,
    )

    image2 = ImageRecord(
        id="image2.jpg",
        path="image2.jpg",
        original_path="image2.jpg",
        filename="image2.jpg",
        width=224,
        height=224,
        format="jpg",
        file_size=100,
    )

    batch = ImageBatch(
        batch_id=1,
        images=[
            image1,
            image2,
        ],
    )

    # Inject fake embedding service.
    embedding_service = FakeEmbeddingService()

    worker = EmbeddingWorker(
        embedding_service=embedding_service
    )

    results = worker.process(
        batch
    )

    # -----------------------------------------
    # Basic result checks
    # -----------------------------------------

    assert len(results) == 2

    assert isinstance(
        results[0],
        ImageEmbedding,
    )

    assert isinstance(
        results[1],
        ImageEmbedding,
    )

    # -----------------------------------------
    # Image IDs
    # -----------------------------------------

    assert results[0].image_id == "image1.jpg"
    assert results[1].image_id == "image2.jpg"

    # -----------------------------------------
    # Embeddings
    # -----------------------------------------

    assert results[0].embedding == [
        1.0,
        0.0,
        0.0,
    ]

    assert results[1].embedding == [
        0.0,
        1.0,
        0.0,
    ]