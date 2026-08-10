from app.analyzers.base import BaseAnalyzer
from app.core.working_dataset import WorkingDataset
from app.models import (
    AnalysisResult,
    Dataset,
    DatasetConfig,
    DatasetType,
    ImageRecord,
)


class TestAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "test"

    def analyze(
        self,
        working_dataset: WorkingDataset,
        config: DatasetConfig,
    ) -> AnalysisResult:

        return AnalysisResult(
            analyzer=self.name,
            images_checked=working_dataset.total_images,
            findings=[],
        )


def test_base_analyzer_contract():

    image = ImageRecord(
        id="image1.jpg",
        path="image1.jpg",
        original_path="image1.jpg",
        filename="image1.jpg",
        width=100,
        height=100,
        format="jpg",
        file_size=1000,
    )

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path="test_dataset",
        images=[image],
    )

    working_dataset = WorkingDataset(dataset)

    analyzer = TestAnalyzer()

    result = analyzer.analyze(
        working_dataset=working_dataset,
        config=DatasetConfig(),
    )

    assert analyzer.name == "test"
    assert result.analyzer == "test"
    assert result.images_checked == 1
    assert result.findings == []