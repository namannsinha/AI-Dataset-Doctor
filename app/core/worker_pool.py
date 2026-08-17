from concurrent.futures import (
    FIRST_COMPLETED,
    ProcessPoolExecutor,
    wait,
)

from app.analyzers.base import BaseAnalyzer
from app.core.worker import Worker
from app.models import AnalysisResult, DatasetConfig
from app.models.ImageBatch import ImageBatch
from app.core.hash_worker import hash_batch
from app.models.hash_result import ImageHash

class WorkerPool:

    def __init__(
        self,
        worker_count: int = 4,
        max_in_flight: int | None = None,
    ):
        if worker_count <= 0:
            raise ValueError(
                "worker_count must be greater than 0"
            )

        if max_in_flight is not None and max_in_flight <= 0:
            raise ValueError(
                "max_in_flight must be greater than 0"
            )

        self.worker_count = worker_count

        self.max_in_flight = (
            max_in_flight
            if max_in_flight is not None
            else worker_count
        )

    def process_batches(
        self,
        batches,
        analyzer: BaseAnalyzer,
        config: DatasetConfig,
    ) -> list[AnalysisResult]:

        results = []

        with ProcessPoolExecutor(
            max_workers=self.worker_count
        ) as executor:

            pending = set()

            for batch in batches:

                future = executor.submit(
                    Worker.process,
                    batch,
                    analyzer,
                    config,
                )

                pending.add(future)

                if len(pending) >= self.max_in_flight:

                    completed, pending = wait(
                        pending,
                        return_when=FIRST_COMPLETED,
                    )

                    for future in completed:
                        results.append(
                            future.result()
                        )

            while pending:

                completed, pending = wait(
                    pending,
                    return_when=FIRST_COMPLETED,
                )

                for future in completed:
                    results.append(
                        future.result()
                    )

        return results

    def process_hash_batches(
        self,
        batches,
    ) -> list[ImageHash]:

        results = []

        with ProcessPoolExecutor(
            max_workers=self.worker_count
        ) as executor:

            pending = {}

            for batch_index, batch in enumerate(batches):

                future = executor.submit(
                    hash_batch,
                    batch,
                )

                pending[future] = batch_index

            ordered_results = [None] * len(pending)

            for future in pending:

                batch_index = pending[future]

                ordered_results[batch_index] = (
                    future.result()
                )

        for batch_results in ordered_results:

            results.extend(batch_results)

        return results