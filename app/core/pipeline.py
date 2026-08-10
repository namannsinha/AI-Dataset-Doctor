from app.analyzers.base import BaseAnalyzer
from app.core.action_policy import ActionPolicy
from app.core.working_dataset import WorkingDataset
from app.models import (
    Action,
    AnalysisResult,
    DatasetConfig,
)
from app.quarantine.quarantine_manager import (
    QuarantineManager,
)


class Pipeline:

    def __init__(
        self,
        analyzers: list[BaseAnalyzer],
        working_dataset: WorkingDataset,
        config: DatasetConfig,
        quarantine_manager: QuarantineManager,
        action_policy: ActionPolicy,
    ):
        self.analyzers = analyzers
        self.working_dataset = working_dataset
        self.config = config
        self.quarantine_manager = quarantine_manager
        self.action_policy = action_policy

    def run(self) -> list[AnalysisResult]:

        results = []

        for analyzer in self.analyzers:

            # -------------------------
            # 1. Run analyzer
            # -------------------------

            result = analyzer.analyze(
                working_dataset=self.working_dataset,
                config=self.config,
            )

            results.append(result)

            # -------------------------
            # 2. Determine action
            # -------------------------

            action = self.action_policy.get_action(
                analyzer.name
            )

            # -------------------------
            # 3. Ignore
            # -------------------------

            if action == Action.IGNORE:
                continue

            # -------------------------
            # 4. Flag
            # -------------------------

            if action == Action.FLAG:
                continue

            # -------------------------
            # 5. Quarantine
            # -------------------------

            if action == Action.QUARANTINE:

                for finding in result.findings:

                    self.quarantine_manager.quarantine(
                        finding=finding,
                        analyzer_name=analyzer.name,
                    )

        return results