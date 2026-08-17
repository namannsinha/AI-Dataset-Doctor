from app.core.batch_manager import BatchManager
from app.core.working_dataset import WorkingDataset
from app.core.embedding_worker import EmbeddingWorker
from app.embeddings.embedding_store import EmbeddingStore
from app.models import DatasetConfig


class EmbeddingPipeline:

    def __init__(
        self,
        worker: EmbeddingWorker | None = None,
        store: EmbeddingStore | None = None,
    ):
        self.worker = (
            worker
            if worker is not None
            else EmbeddingWorker()
        )

        self.store = store

    def run(
        self,
        working_dataset: WorkingDataset,
        config: DatasetConfig,
    ) -> EmbeddingStore:

        if self.store is None:
            raise ValueError(
                "EmbeddingStore must be provided "
                "to EmbeddingPipeline."
            )

        # -----------------------------------------
        # 1. Clear previous embedding data
        # -----------------------------------------

        self.store.clear()

        # -----------------------------------------
        # 2. Stream active images
        # -----------------------------------------

        images = working_dataset.iter_images()

        # -----------------------------------------
        # 3. Create batches
        # -----------------------------------------

        batch_manager = BatchManager(
            images=images,
            batch_size=config.batch_size,
        )

        # -----------------------------------------
        # 4. Process batches
        # -----------------------------------------

        for batch in batch_manager:

            batch_results = self.worker.process(
                batch
            )

            # -----------------------------------------
            # 5. Extract data for storage
            # -----------------------------------------

            if not batch_results:
                continue

            embeddings = [
                result.embedding
                for result in batch_results
            ]

            image_ids = [
                result.image_id
                for result in batch_results
            ]

            labels = [
                result.label
                for result in batch_results
            ]

            # -----------------------------------------
            # 6. Store batch immediately
            # -----------------------------------------

            self.store.append(
                embeddings=embeddings,
                image_ids=image_ids,
                labels=labels,
            )

        # -----------------------------------------
        # 7. Return the store
        # -----------------------------------------

        return self.store