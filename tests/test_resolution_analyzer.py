from app.analyzers.resolution import ResolutionAnalyzer
from app.core.working_dataset import WorkingDataset
from app.models import (
    Dataset,
    DatasetConfig,
    DatasetType,
    ImageRecord,
)


def create_image_record(
    name,
    width,
    height,
    tmp_path,
):

    path = tmp_path / name

    path.write_bytes(b"test")

    return ImageRecord(
        id=name,
        path=str(path),
        original_path=name,
        filename=name,
        width=width,
        height=height,
        format="jpg",
        file_size=path.stat().st_size,
    )


def create_dataset(images, tmp_path):

    return Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(tmp_path),
        images=images,
    )


def test_resolution_analyzer_detects_low_resolution(
    tmp_path,
):

    images = [
        create_image_record(
            "good.jpg",
            512,
            512,
            tmp_path,
        ),
        create_image_record(
            "small.jpg",
            128,
            128,
            tmp_path,
        ),
    ]

    dataset = create_dataset(
        images,
        tmp_path,
    )

    working_dataset = WorkingDataset(dataset)

    config = DatasetConfig(
        min_width=224,
        min_height=224,
    )

    result = ResolutionAnalyzer().analyze(
        working_dataset=working_dataset,
        config=config,
    )

    assert result.analyzer == "resolution"

    assert result.images_checked == 2

    assert result.issues_found == 1

    finding = result.findings[0]

    assert finding.image_id == "small.jpg"

    assert finding.issue_type == "low_resolution"

def test_resolution_checks_width_and_height(
    tmp_path,
):

    images = [
        create_image_record(
            "small_width.jpg",
            100,
            500,
            tmp_path,
        ),
        create_image_record(
            "small_height.jpg",
            500,
            100,
            tmp_path,
        ),
        create_image_record(
            "valid.jpg",
            500,
            500,
            tmp_path,
        ),
    ]

    dataset = create_dataset(
        images,
        tmp_path,
    )

    working_dataset = WorkingDataset(dataset)

    config = DatasetConfig(
        min_width=224,
        min_height=224,
    )

    result = ResolutionAnalyzer().analyze(
        working_dataset=working_dataset,
        config=config,
    )

    assert result.issues_found == 2

    finding_ids = {
        finding.image_id
        for finding in result.findings
    }

    assert "small_width.jpg" in finding_ids
    assert "small_height.jpg" in finding_ids
    assert "valid.jpg" not in finding_ids

def test_exact_minimum_resolution_passes(
    tmp_path,
):

    image = create_image_record(
        "exact.jpg",
        224,
        224,
        tmp_path,
    )

    dataset = create_dataset(
        [image],
        tmp_path,
    )

    working_dataset = WorkingDataset(dataset)

    config = DatasetConfig(
        min_width=224,
        min_height=224,
    )

    result = ResolutionAnalyzer().analyze(
        working_dataset=working_dataset,
        config=config,
    )

    assert result.issues_found == 0