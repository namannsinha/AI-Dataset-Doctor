from PIL import Image

from app.analyzers.corruption import CorruptionAnalyzer
from app.core.analyzer_runner import run_analyzer
from app.core.working_dataset import WorkingDataset
from app.models import (
    Dataset,
    DatasetConfig,
    DatasetType,
    ImageRecord,
)
from app.quarantine.quarantine_manager import (
    QuarantineManager,
)


def create_valid_image(path):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = Image.new(
        "RGB",
        (100, 100),
    )

    image.save(path)


def create_corrupted_file(path):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_bytes(
        b"not an actual image"
    )


def test_corruption_end_to_end(tmp_path):

    # -------------------------
    # Create dataset
    # -------------------------

    dataset_root = tmp_path / "dataset"

    valid_path = (
        dataset_root / "good.jpg"
    )

    corrupted_path = (
        dataset_root / "bad.jpg"
    )

    create_valid_image(valid_path)

    create_corrupted_file(
        corrupted_path
    )

    # -------------------------
    # Create records
    # -------------------------

    valid_image = ImageRecord(
        id="good.jpg",
        path=str(valid_path),
        original_path="good.jpg",
        filename="good.jpg",
        width=100,
        height=100,
        format="jpg",
        file_size=valid_path.stat().st_size,
    )

    corrupted_image = ImageRecord(
        id="bad.jpg",
        path=str(corrupted_path),
        original_path="bad.jpg",
        filename="bad.jpg",
        width=None,
        height=None,
        format="jpg",
        file_size=corrupted_path.stat().st_size,
    )

    # -------------------------
    # Create dataset
    # -------------------------

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(dataset_root),
        images=[
            valid_image,
            corrupted_image,
        ],
    )

    working_dataset = WorkingDataset(
        dataset
    )

    # -------------------------
    # Create manager
    # -------------------------

    output_root = tmp_path / "output"

    quarantine_manager = (
        QuarantineManager(
            output_root=str(output_root),
            working_dataset=working_dataset,
        )
    )

    # -------------------------
    # Run analyzer
    # -------------------------

    analyzer = CorruptionAnalyzer()

    result = run_analyzer(
        analyzer=analyzer,
        working_dataset=working_dataset,
        config=DatasetConfig(),
        quarantine_manager=quarantine_manager,
    )

    # -------------------------
    # Verify analysis
    # -------------------------

    assert result.analyzer == "corruption"

    assert result.images_checked == 2

    assert result.issues_found == 1

    # -------------------------
    # Verify filesystem
    # -------------------------

    assert valid_path.exists()

    assert not corrupted_path.exists()

    quarantine_path = (
        output_root
        / "Quarantine"
        / "corruption"
        / "bad.jpg"
    )

    assert quarantine_path.exists()

    # -------------------------
    # Verify WorkingDataset
    # -------------------------

    assert working_dataset.total_images == 1

    assert working_dataset.contains(
        "good.jpg"
    )

    assert not working_dataset.contains(
        "bad.jpg"
    )

    # -------------------------
    # Original Dataset unchanged
    # -------------------------

    assert len(dataset.images) == 2