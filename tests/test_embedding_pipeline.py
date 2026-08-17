from types import SimpleNamespace

from app.embeddings.embedding_pipeline import EmbeddingPipeline
from app.embeddings.embedding_store import EmbeddingStore
from app.models import DatasetConfig, ImageEmbedding


class FakeEmbeddingWorker:

    def process(self, batch):

        results = []

        for image in batch.images:

            results.append(
                ImageEmbedding(
                    image_id=image.id,
                    label=image.label,
                    embedding=[
                        1.0,
                        0.0,
                        0.0,
                    ],
                )
            )

        return results


class FakeWorkingDataset:

    def __init__(self, images):

        self.images = images

    def iter_images(self):

        return iter(self.images)

    @property
    def total_images(self):

        return len(self.images)


def test_embedding_pipeline(
    tmp_path,
):

    # -----------------------------------------
    # Arrange
    # -----------------------------------------

    images = [
        SimpleNamespace(
            id="image1.jpg",
            label="cat",
        ),
        SimpleNamespace(
            id="image2.jpg",
            label="dog",
        ),
        SimpleNamespace(
            id="image3.jpg",
            label=None,
        ),
        SimpleNamespace(
            id="image4.jpg",
            label="cat",
        ),
    ]

    working_dataset = FakeWorkingDataset(
        images
    )

    store = EmbeddingStore(
        output_root=str(tmp_path),
    )

    worker = FakeEmbeddingWorker()

    pipeline = EmbeddingPipeline(
        worker=worker,
        store=store,
    )

    config = DatasetConfig(
        batch_size=2,
    )

    # -----------------------------------------
    # Act
    # -----------------------------------------

    result = pipeline.run(
        working_dataset=working_dataset,
        config=config,
    )

    # -----------------------------------------
    # Assert
    # -----------------------------------------

    assert result is store

    embeddings, image_ids, labels = (
        store.load()
    )

    assert len(embeddings) == 4

    assert image_ids == [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
        "image4.jpg",
    ]

    assert labels == [
        "cat",
        "dog",
        None,
        "cat",
    ]

    assert embeddings.shape == (
        4,
        3,
    )