from app.analyzers.base import BaseAnalyzer
from app.models import AnalysisResult, DatasetConfig, ImageBatch


class Worker:

    @staticmethod
    def process(
        batch: ImageBatch,
        analyzer: BaseAnalyzer,
        config: DatasetConfig,
    ) -> AnalysisResult:

        return analyzer.analyze(
            working_dataset=batch,
            config=config,
        )