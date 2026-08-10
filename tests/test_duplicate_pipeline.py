from app.analyzers.duplicate import DuplicateAnalyzer
from app.core.action_policy import ActionPolicy
from app.core.pipeline import Pipeline
from app.core.working_dataset import WorkingDataset
from app.models import (
    Action,
    Dataset,
    DatasetConfig,
    DatasetType,
    ImageRecord,
)
from app.quarantine.quarantine_manager import QuarantineManager


def create_image_record(path):

    return ImageRecord(
        id=path.name,
        path=str(path),
        original_path=path.name,
        filename=path.name,
        width=100,
        height=100,
        format="jpg",
        file_size=path.stat().st_size,
    )


def create_duplicate_dataset(tmp_path):

    dataset_root = tmp_path / "dataset"

    original = dataset_root / "cat.jpg"
    duplicate = dataset_root / "cat_copy.jpg"
    unique = dataset_root / "dog.jpg"

    original.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    original.write_bytes(b"same image")
    duplicate.write_bytes(b"same image")
    unique.write_bytes(b"different image")

    images = [
        create_image_record(original),
        create_image_record(duplicate),
        create_image_record(unique),
    ]

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(dataset_root),
        images=images,
    )

    return dataset


def test_duplicate_flag_keeps_files(tmp_path):

    dataset = create_duplicate_dataset(tmp_path)

    working_dataset = WorkingDataset(dataset)

    output_root = tmp_path / "output"

    quarantine_manager = QuarantineManager(
        output_root=str(output_root),
        working_dataset=working_dataset,
    )

    pipeline = Pipeline(
        analyzers=[
            DuplicateAnalyzer(),
        ],
        working_dataset=working_dataset,
        config=DatasetConfig(),
        quarantine_manager=quarantine_manager,
        action_policy=ActionPolicy(
            analyzer_actions={
                "duplicate": Action.FLAG,
            }
        ),
    )

    results = pipeline.run()

    # One duplicate was detected.
    assert results[0].issues_found == 1

    # Nothing was removed.
    assert working_dataset.total_images == 3

    # Both duplicate files still exist.
    assert (
        tmp_path
        / "dataset"
        / "cat.jpg"
    ).exists()

    assert (
        tmp_path
        / "dataset"
        / "cat_copy.jpg"
    ).exists()


def test_duplicate_quarantine_removes_duplicate(
    tmp_path,
):

    dataset = create_duplicate_dataset(tmp_path)

    working_dataset = WorkingDataset(dataset)

    output_root = tmp_path / "output"

    quarantine_manager = QuarantineManager(
        output_root=str(output_root),
        working_dataset=working_dataset,
    )

    pipeline = Pipeline(
        analyzers=[
            DuplicateAnalyzer(),
        ],
        working_dataset=working_dataset,
        config=DatasetConfig(),
        quarantine_manager=quarantine_manager,
        action_policy=ActionPolicy(
            analyzer_actions={
                "duplicate": Action.QUARANTINE,
            }
        ),
    )

    results = pipeline.run()

    # One duplicate was detected.
    assert results[0].issues_found == 1

    # Original + unique image remain.
    assert working_dataset.total_images == 2

    # Original remains.
    assert (
        tmp_path
        / "dataset"
        / "cat.jpg"
    ).exists()

    # Duplicate was moved.
    assert not (
        tmp_path
        / "dataset"
        / "cat_copy.jpg"
    ).exists()

    # Duplicate exists in quarantine.
    quarantine_file = (
        output_root
        / "Quarantine"
        / "duplicate"
        / "cat_copy.jpg"
    )

    assert quarantine_file.exists()

    # Unique image remains.
    assert (
        tmp_path
        / "dataset"
        / "dog.jpg"
    ).exists()