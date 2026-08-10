from app.analyzers.duplicate import DuplicateAnalyzer
from app.core.working_dataset import WorkingDataset
from app.models import (
    Dataset,
    DatasetConfig,
    DatasetType,
    ImageRecord,
)

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

def test_detects_exact_duplicate(tmp_path):

    file1 = tmp_path / "cat.jpg"
    file2 = tmp_path / "cat_copy.jpg"

    content = b"identical image content"

    file1.write_bytes(content)
    file2.write_bytes(content)

    images = [
        create_image_record(file1),
        create_image_record(file2),
    ]

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(tmp_path),
        images=images,
    )

    working_dataset = WorkingDataset(
        dataset
    )

    analyzer = DuplicateAnalyzer()

    result = analyzer.analyze(
        working_dataset=working_dataset,
        config=DatasetConfig(),
    )

    assert result.analyzer == "duplicate"

    assert result.images_checked == 2

    assert result.issues_found == 1

    finding = result.findings[0]

    assert finding.image_id == "cat_copy.jpg"

    assert finding.issue_type == "duplicate"

    assert "cat.jpg" in finding.reason

def test_unique_images_are_not_flagged(tmp_path):

    file1 = tmp_path / "cat.jpg"
    file2 = tmp_path / "dog.jpg"

    file1.write_bytes(b"cat content")
    file2.write_bytes(b"dog content")

    images = [
        create_image_record(file1),
        create_image_record(file2),
    ]

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(tmp_path),
        images=images,
    )

    working_dataset = WorkingDataset(
        dataset
    )

    analyzer = DuplicateAnalyzer()

    result = analyzer.analyze(
        working_dataset=working_dataset,
        config=DatasetConfig(),
    )

    assert result.images_checked == 2

    assert result.issues_found == 0

    assert result.findings == []

def test_detects_multiple_duplicates(tmp_path):

    files = [
        tmp_path / "cat1.jpg",
        tmp_path / "cat2.jpg",
        tmp_path / "cat3.jpg",
    ]

    content = b"same image"

    for file in files:
        file.write_bytes(content)

    images = [
        create_image_record(file)
        for file in files
    ]

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(tmp_path),
        images=images,
    )

    working_dataset = WorkingDataset(
        dataset
    )

    analyzer = DuplicateAnalyzer()

    result = analyzer.analyze(
        working_dataset=working_dataset,
        config=DatasetConfig(),
    )

    assert result.images_checked == 3

    assert result.issues_found == 2

def test_filename_does_not_affect_duplicate_detection(
    tmp_path,
):

    original = (
        tmp_path
        / "random_filename_123.jpg"
    )

    copy = (
        tmp_path
        / "completely_different_name.jpg"
    )

    content = b"same content"

    original.write_bytes(content)
    copy.write_bytes(content)

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(tmp_path),
        images=[
            create_image_record(original),
            create_image_record(copy),
        ],
    )

    working_dataset = WorkingDataset(
        dataset
    )

    result = DuplicateAnalyzer().analyze(
        working_dataset=working_dataset,
        config=DatasetConfig(),
    )

    assert result.issues_found == 1