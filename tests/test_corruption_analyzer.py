from PIL import Image

from app.analyzers.corruption import CorruptionAnalyzer
from app.core.working_dataset import WorkingDataset
from app.models import (
    Dataset,
    DatasetConfig,
    DatasetType,
    ImageRecord,
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


def create_corrupted_image(path):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_bytes(
        b"This is not a valid image"
    )


def create_dataset(tmp_path):

    valid_path = (
        tmp_path
        / "valid.jpg"
    )

    corrupted_path = (
        tmp_path
        / "corrupted.jpg"
    )

    create_valid_image(valid_path)

    create_corrupted_image(
        corrupted_path
    )

    valid_image = ImageRecord(
        id="valid.jpg",
        path=str(valid_path),
        original_path="valid.jpg",
        filename="valid.jpg",
        width=100,
        height=100,
        format="jpg",
        file_size=valid_path.stat().st_size,
    )

    corrupted_image = ImageRecord(
        id="corrupted.jpg",
        path=str(corrupted_path),
        original_path="corrupted.jpg",
        filename="corrupted.jpg",
        width=None,
        height=None,
        format="jpg",
        file_size=corrupted_path.stat().st_size,
    )

    dataset = Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(tmp_path),
        images=[
            valid_image,
            corrupted_image,
        ],
    )

    return dataset


def test_corruption_analyzer(tmp_path):

    dataset = create_dataset(tmp_path)

    working_dataset = WorkingDataset(
        dataset
    )

    analyzer = CorruptionAnalyzer()

    result = analyzer.analyze(
        working_dataset=working_dataset,
        config=DatasetConfig(),
    )

    assert result.analyzer == "corruption"

    assert result.images_checked == 2

    assert result.issues_found == 1

    finding = result.findings[0]

    assert finding.image_id == "corrupted.jpg"

    assert finding.issue_type == "corruption"

    assert finding.severity == "high"


def test_valid_images_are_not_flagged(tmp_path):

    dataset = create_dataset(tmp_path)

    working_dataset = WorkingDataset(
        dataset
    )

    analyzer = CorruptionAnalyzer()

    result = analyzer.analyze(
        working_dataset=working_dataset,
        config=DatasetConfig(),
    )

    finding_ids = {
        finding.image_id
        for finding in result.findings
    }

    assert "valid.jpg" not in finding_ids