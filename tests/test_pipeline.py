from app.analyzers.base import BaseAnalyzer
from app.core.pipeline import Pipeline
from app.core.working_dataset import WorkingDataset
from app.core.action_policy import ActionPolicy
from app.models import Action
from app.models import (
    AnalysisResult,
    Dataset,
    DatasetConfig,
    DatasetType,
    Finding,
    ImageRecord,
)
from app.quarantine.quarantine_manager import QuarantineManager


class RemoveOneAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "remove_one"

    def analyze(
        self,
        working_dataset: WorkingDataset,
        config: DatasetConfig,
    ) -> AnalysisResult:

        image = working_dataset.images[0]

        finding = Finding(
            image_id=image.id,
            issue_type="test",
            severity="low",
            reason="Test removal",
        )

        return AnalysisResult(
            analyzer=self.name,
            images_checked=working_dataset.total_images,
            findings=[finding],
        )


class ObserveAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "observe"

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


def test_pipeline_is_sequential(tmp_path):

    # -------------------------
    # Create fake image files
    # -------------------------

    dataset_root = tmp_path / "dataset"

    images = []

    for name in ["image1.jpg", "image2.jpg"]:

        path = dataset_root / name

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            b"test image"
        )

        images.append(
            ImageRecord(
                id=name,
                path=str(path),
                original_path=name,
                filename=name,
                width=100,
                height=100,
                format="jpg",
                file_size=path.stat().st_size,
            )
        )

    # -------------------------
    # Create Dataset
    # -------------------------

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(dataset_root),
        images=images,
    )

    working_dataset = WorkingDataset(dataset)

    # -------------------------
    # Quarantine Manager
    # -------------------------

    output_root = tmp_path / "output"

    quarantine_manager = QuarantineManager(
        output_root=str(output_root),
        working_dataset=working_dataset,
    )

    # -------------------------
    # Pipeline
    # -------------------------

    pipeline = Pipeline(
        analyzers=[
            RemoveOneAnalyzer(),
            ObserveAnalyzer(),
        ],
        working_dataset=working_dataset,
        config=DatasetConfig(),
        quarantine_manager=quarantine_manager,
        action_policy=ActionPolicy(
            analyzer_actions={
                "remove_one": Action.QUARANTINE,
                "observe": Action.FLAG,
            }
        ),
    )

    results = pipeline.run()

    # -------------------------
    # First analyzer
    # -------------------------

    assert results[0].images_checked == 2
    assert results[0].issues_found == 1

    # -------------------------
    # Second analyzer
    # -------------------------

    # It should see only one image.
    assert results[1].images_checked == 1

    # -------------------------
    # Final state
    # -------------------------

    assert working_dataset.total_images == 1

def test_pipeline_flag_does_not_remove_image(tmp_path):

    dataset_root = tmp_path / "dataset"

    image_path = dataset_root / "image.jpg"

    image_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_path.write_bytes(
        b"test image"
    )

    image = ImageRecord(
        id="image.jpg",
        path=str(image_path),
        original_path="image.jpg",
        filename="image.jpg",
        width=100,
        height=100,
        format="jpg",
        file_size=image_path.stat().st_size,
    )

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(dataset_root),
        images=[image],
    )

    working_dataset = WorkingDataset(dataset)

    output_root = tmp_path / "output"

    quarantine_manager = QuarantineManager(
        output_root=str(output_root),
        working_dataset=working_dataset,
    )

    pipeline = Pipeline(
        analyzers=[
            RemoveOneAnalyzer(),
        ],
        working_dataset=working_dataset,
        config=DatasetConfig(),
        quarantine_manager=quarantine_manager,
        action_policy=ActionPolicy(
            analyzer_actions={
                "remove_one": Action.FLAG,
            }
        ),
    )

    results = pipeline.run()

    # Finding exists
    assert results[0].issues_found == 1

    # But image remains
    assert working_dataset.total_images == 1

    # Physical file remains
    assert image_path.exists()

    # Nothing was quarantined
    quarantine_root = output_root / "Quarantine"

    if quarantine_root.exists():
        assert not any(
            path.is_file()
            for path in quarantine_root.rglob("*")
        )

def test_pipeline_ignore_does_not_remove_image(tmp_path):

    dataset_root = tmp_path / "dataset"

    image_path = dataset_root / "image.jpg"

    image_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_path.write_bytes(
        b"test image"
    )

    image = ImageRecord(
        id="image.jpg",
        path=str(image_path),
        original_path="image.jpg",
        filename="image.jpg",
        width=100,
        height=100,
        format="jpg",
        file_size=image_path.stat().st_size,
    )

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(dataset_root),
        images=[image],
    )

    working_dataset = WorkingDataset(dataset)

    output_root = tmp_path / "output"

    quarantine_manager = QuarantineManager(
        output_root=str(output_root),
        working_dataset=working_dataset,
    )

    pipeline = Pipeline(
        analyzers=[
            RemoveOneAnalyzer(),
        ],
        working_dataset=working_dataset,
        config=DatasetConfig(),
        quarantine_manager=quarantine_manager,
        action_policy=ActionPolicy(
            analyzer_actions={
                "remove_one": Action.IGNORE,
            }
        ),
    )

    results = pipeline.run()

    # Analyzer still found the issue
    assert results[0].issues_found == 1

    # But nothing happened to the dataset
    assert working_dataset.total_images == 1

    assert image_path.exists()

    quarantine_root = output_root / "Quarantine"

    if quarantine_root.exists():
        assert not any(
            path.is_file()
            for path in quarantine_root.rglob("*")
        )