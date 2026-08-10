from app.analyzers.base import BaseAnalyzer
from app.core.working_dataset import WorkingDataset
from app.models import AnalysisResult, DatasetConfig
from app.quarantine.quarantine_manager import QuarantineManager


def run_analyzer(
    analyzer: BaseAnalyzer,
    working_dataset: WorkingDataset,
    config: DatasetConfig,
    quarantine_manager: QuarantineManager,
) -> AnalysisResult:

    # 1. Analyze the currently active dataset
    result = analyzer.analyze(
        working_dataset=working_dataset,
        config=config,
    )

    # 2. Quarantine every detected issue
    for finding in result.findings:
        quarantine_manager.quarantine(
            finding=finding,
            analyzer_name=analyzer.name,
        )

    return result