from app.embeddings.embedding_service import EmbeddingService
from app.models import ImageEmbedding
from app.models.ImageBatch import ImageBatch


class EmbeddingWorker:

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
    ):
        self.embedding_service = (
            embedding_service
            if embedding_service is not None
            else EmbeddingService()
        )

    def process(
        self,
        batch: ImageBatch,
    ) -> list[ImageEmbedding]:

        results = []

        for image in batch.images:

            try:
                embedding = (
                    self.embedding_service.generate_embedding(
                        image.path
                    )
                )

            except Exception as exc:

                print(
                    f"Could not generate embedding "
                    f"for {image.path}: {exc}"
                )

                continue

            results.append(
                ImageEmbedding(
                    image_id=image.id,
                    label=image.label,
                    embedding=(
                        embedding.tolist()
                        if hasattr(embedding, "tolist")
                        else list(embedding)
                    ),
                )
            )

        return results