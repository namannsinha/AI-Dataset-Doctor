from pathlib import Path

from app.embeddings.embedding_service import (
    EmbeddingService,
)


def test_embedding_service():

    image_path = next(
        Path(
            "data/input/practice_dataset"
        ).glob("*.jpg")
    )

    service = EmbeddingService()

    embeddings = service.embed_images(
        [str(image_path)]
    )

    assert embeddings.shape[0] == 1

    assert embeddings.shape[1] > 0