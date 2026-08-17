from app.analyzers.base import BaseAnalyzer
from app.core.action_policy import ActionPolicy
from app.core.working_dataset import WorkingDataset
from app.core.batch_manager import BatchManager
from app.core.worker_pool import WorkerPool
from app.models import (
    Action,
    AnalysisResult,
    DatasetConfig,
)
from app.quarantine.quarantine_manager import (
    QuarantineManager,
)
from app.analyzers.duplicate import DuplicateAnalyzer


class Pipeline:

    def __init__(
        self,
        analyzers: list[BaseAnalyzer],
        working_dataset: WorkingDataset,
        config: DatasetConfig,
        quarantine_manager: QuarantineManager,
        action_policy: ActionPolicy,
        worker_pool: WorkerPool | None = None,
    ):
        self.analyzers = analyzers
        self.working_dataset = working_dataset
        self.config = config
        self.quarantine_manager = quarantine_manager
        self.action_policy = action_policy

        self.worker_pool = (
            worker_pool
            if worker_pool is not None
            else WorkerPool(
                worker_count=4,
            )
        )
    def run(self) -> list[AnalysisResult]:
        results = []

        for analyzer in self.analyzers:

            # -------------------------
            # 1. Stream active images
            # -------------------------

            images = self.working_dataset.iter_images()

            # -------------------------
            # 2. Create batches
            # -------------------------

            batch_manager = BatchManager(
                images=images,
                batch_size=self.config.batch_size,
            )

            # -------------------------
            # 3. Process analyzer
            # -------------------------

            if isinstance(analyzer, DuplicateAnalyzer):

                hash_results = (
                    self.worker_pool.process_hash_batches(
                        batches=batch_manager,
                    )
                )

                findings = analyzer.process_hashes(
                    hash_results
                )

                combined_result = AnalysisResult(
                    analyzer=analyzer.name,
                    images_checked=len(hash_results),
                    findings=findings,
                )

            else:

                batch_results = (
                    self.worker_pool.process_batches(
                        batches=batch_manager,
                        analyzer=analyzer,
                        config=self.config,
                    )
                )

                combined_result = AnalysisResult(
                    analyzer=analyzer.name,
                    images_checked=sum(
                        result.images_checked
                        for result in batch_results
                    ),
                    findings=[
                        finding
                        for result in batch_results
                        for finding in result.findings
                    ],
                )

            # -------------------------
            # 4. Store result
            # -------------------------

            results.append(combined_result)

            # -------------------------
            # 5. Determine action
            # -------------------------

            action = self.action_policy.get_action(
                analyzer.name
            )

            # -------------------------
            # 6. Ignore
            # -------------------------

            if action == Action.IGNORE:
                continue

            # -------------------------
            # 7. Flag
            # -------------------------

            if action == Action.FLAG:
                continue

            # -------------------------
            # 8. Quarantine
            # -------------------------

            if action == Action.QUARANTINE:

                for finding in combined_result.findings:

                    self.quarantine_manager.quarantine(
                        finding=finding,
                        analyzer_name=analyzer.name,
                    )

        return results