from abc import ABC, abstractmethod

from app.core.working_dataset import WorkingDataset
from app.models import AnalysisResult, DatasetConfig


class BaseAnalyzer(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique name of the analyzer.
        """
        pass

    @abstractmethod
    def analyze(
        self,
        working_dataset: WorkingDataset,
        config: DatasetConfig,
    ) -> AnalysisResult:
        """
        Analyze the currently active dataset and
        return the analysis result.
        """
        pass