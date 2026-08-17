from app.core.worker_pool import WorkerPool
from app.models import (
    AnalysisResult,
    DatasetConfig,
    ImageRecord,
)
from app.models.ImageBatch import ImageBatch
from app.analyzers.base import BaseAnalyzer


class TestPoolAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "test_pool"

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


def create_images(count: int) -> list[ImageRecord]:

    return [
        ImageRecord(
            id=f"image_{i}.jpg",
            path=f"/dataset/image_{i}.jpg",
            original_path=f"image_{i}.jpg",
            filename=f"image_{i}.jpg",
            width=100,
            height=100,
            format="jpg",
            file_size=100,
        )
        for i in range(count)
    ]


def test_worker_pool_processes_batches():

    images = create_images(6)

    batches = [
        ImageBatch(
            batch_id=1,
            images=images[:2],
        ),
        ImageBatch(
            batch_id=2,
            images=images[2:4],
        ),
        ImageBatch(
            batch_id=3,
            images=images[4:6],
        ),
    ]

    pool = WorkerPool(
        worker_count=2
    )

    results = pool.process_batches(
        batches=batches,
        analyzer=TestPoolAnalyzer(),
        config=DatasetConfig(),
    )

    assert len(results) == 3

    assert results[0].images_checked == 2
    assert results[1].images_checked == 2
    assert results[2].images_checked == 2

    assert all(
        result.analyzer == "test_pool"
        for result in results
    )

def test_worker_pool_rejects_invalid_max_in_flight():

    try:
        WorkerPool(
            worker_count=2,
            max_in_flight=0,
        )

        assert False

    except ValueError:
        assert True

def test_worker_pool_accepts_generator():

    images = create_images(6)

    batches = (
        ImageBatch(
            batch_id=i + 1,
            images=images[i:i + 2],
        )
        for i in range(0, 6, 2)
    )

    pool = WorkerPool(
        worker_count=2,
        max_in_flight=2,
    )

    results = pool.process_batches(
        batches=batches,
        analyzer=TestPoolAnalyzer(),
        config=DatasetConfig(),
    )

    assert len(results) == 3

    assert sum(
        result.images_checked
        for result in results
    ) == 6