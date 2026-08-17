from app.core.worker import Worker
from app.models import (
    AnalysisResult,
    DatasetConfig,
    ImageRecord,
)
from app.models.ImageBatch import ImageBatch
from app.analyzers.base import BaseAnalyzer


class TestAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "test"

    def analyze(
        self,
        working_dataset,
        config: DatasetConfig,
    ) -> AnalysisResult:

        return AnalysisResult(
            analyzer=self.name,
            images_checked=working_dataset.total_images,
            findings=[],
        )


def test_worker_processes_batch():

    images = [
        ImageRecord(
            id="image1.jpg",
            path="/dataset/image1.jpg",
            original_path="image1.jpg",
            filename="image1.jpg",
            width=100,
            height=100,
            format="jpg",
            file_size=100,
        ),
        ImageRecord(
            id="image2.jpg",
            path="/dataset/image2.jpg",
            original_path="image2.jpg",
            filename="image2.jpg",
            width=100,
            height=100,
            format="jpg",
            file_size=100,
        ),
    ]

    batch = ImageBatch(
        batch_id=1,
        images=images,
    )

    analyzer = TestAnalyzer()

    result = Worker.process(
        batch=batch,
        analyzer=analyzer,
        config=DatasetConfig(),
    )

    assert result.analyzer == "test"
    assert result.images_checked == 2
    assert result.issues_found == 0