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

        if not batch.images:
            return []

        # -----------------------------------------
        # 1. Collect image paths
        # -----------------------------------------

        image_paths = [
            image.path
            for image in batch.images
        ]

        # -----------------------------------------
        # 2. Generate embeddings as one batch
        # -----------------------------------------

        embeddings, valid_paths = (
            self.embedding_service
            .generate_embeddings(
                image_paths
            )
        )

        # -----------------------------------------
        # 3. Map paths back to ImageRecords
        # -----------------------------------------

        path_to_image = {
            image.path: image
            for image in batch.images
        }

        results = []

        for embedding, image_path in zip(
            embeddings,
            valid_paths,
        ):

            image = path_to_image.get(
                image_path
            )

            if image is None:
                continue

            results.append(
                ImageEmbedding(
                    image_id=image.id,
                    label=image.label,
                    embedding=(
                        embedding.tolist()
                        if hasattr(
                            embedding,
                            "tolist",
                        )
                        else list(embedding)
                    ),
                )
            )

        return results