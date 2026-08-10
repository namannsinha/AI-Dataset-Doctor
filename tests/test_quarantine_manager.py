from app.core.working_dataset import WorkingDataset
from app.models import (
    Dataset,
    DatasetType,
    Finding,
    ImageRecord,
)
from app.quarantine.quarantine_manager import (
    QuarantineManager,
)


def test_quarantine_moves_image(tmp_path):

    # -------------------------
    # Create fake dataset
    # -------------------------

    dataset_root = tmp_path / "dataset"

    image_path = (
        dataset_root
        / "train"
        / "cat"
        / "cat1.jpg"
    )

    image_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_path.write_bytes(
        b"fake image data"
    )

    # -------------------------
    # Create ImageRecord
    # -------------------------

    image = ImageRecord(
        id="train/cat/cat1.jpg",
        path=str(image_path),
        original_path="train/cat/cat1.jpg",
        filename="cat1.jpg",
        label="cat",
        split="train",
        width=100,
        height=100,
        format="jpg",
        file_size=image_path.stat().st_size,
    )

    # -------------------------
    # Create Dataset
    # -------------------------

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.TRAIN_TEST,
        source_format="folder",
        root_path=str(dataset_root),
        images=[image],
        classes=["cat"],
        splits=["train"],
    )

    working_dataset = WorkingDataset(dataset)

    # -------------------------
    # Create Manager
    # -------------------------

    output_root = tmp_path / "output"

    manager = QuarantineManager(
        output_root=str(output_root),
        working_dataset=working_dataset,
    )

    # -------------------------
    # Create Finding
    # -------------------------

    finding = Finding(
        image_id="train/cat/cat1.jpg",
        issue_type="blur",
        severity="medium",
        reason="Image is too blurry",
        value=40.0,
        threshold=60.0,
    )

    # -------------------------
    # Quarantine
    # -------------------------

    record = manager.quarantine(
        finding=finding,
        analyzer_name="BlurAnalyzer",
    )

    # -------------------------
    # Verify physical movement
    # -------------------------

    assert not image_path.exists()

    quarantine_path = (
        output_root
        / "Quarantine"
        / "bluranalyzer"
        / "train"
        / "cat"
        / "cat1.jpg"
    )

    assert quarantine_path.exists()

    # -------------------------
    # Verify WorkingDataset
    # -------------------------

    assert working_dataset.total_images == 0

    # -------------------------
    # Verify original Dataset
    # -------------------------

    assert len(dataset.images) == 1

    # -------------------------
    # Verify QuarantineRecord
    # -------------------------

    assert record.image_id == "train/cat/cat1.jpg"

    assert record.reason == "Image is too blurry"

    assert record.analyzer == "BlurAnalyzer"