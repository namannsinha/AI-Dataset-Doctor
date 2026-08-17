from PIL import Image, ImageFilter

from app.analyzers.blur import BlurAnalyzer
from app.core.working_dataset import WorkingDataset
from app.models import (
    Dataset,
    DatasetConfig,
    DatasetType,
    ImageRecord,
)


def create_image_record(
    image_path,
    image_id,
):
    return ImageRecord(
        id=image_id,
        path=str(image_path),
        original_path=image_id,
        filename=image_id,
        width=100,
        height=100,
        format="jpg",
        file_size=image_path.stat().st_size,
    )


def create_dataset(
    images,
    tmp_path,
):
    return Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(tmp_path),
        images=images,
    )


def test_blur_analyzer_detects_blurry_image(tmp_path):

    image_path = tmp_path / "blurry.jpg"

    # Create a simple image
    image = Image.new(
        "RGB",
        (100, 100),
        "white",
    )

    # Add blur
    image = image.filter(
        ImageFilter.GaussianBlur(radius=10)
    )

    image.save(image_path)

    image_record = create_image_record(
        image_path,
        "blurry.jpg",
    )

    dataset = create_dataset(
        [image_record],
        tmp_path,
    )

    working_dataset = WorkingDataset(dataset)

    config = DatasetConfig(
        blur_threshold=60.0,
    )

    result = BlurAnalyzer().analyze(
        working_dataset=working_dataset,
        config=config,
    )

    assert result.analyzer == "blur"
    assert result.images_checked == 1
    assert result.issues_found == 1

    finding = result.findings[0]

    assert finding.image_id == "blurry.jpg"
    assert finding.issue_type == "blur"
    assert finding.severity == "medium"


def test_blur_analyzer_does_not_flag_sharp_image(tmp_path):

    image_path = tmp_path / "sharp.jpg"

    # Create an image with strong edges.
    image = Image.new(
        "RGB",
        (100, 100),
        "white",
    )

    pixels = image.load()

    for x in range(100):
        for y in range(100):

            if (x // 10 + y // 10) % 2 == 0:
                pixels[x, y] = (0, 0, 0)

    image.save(image_path)

    image_record = create_image_record(
        image_path,
        "sharp.jpg",
    )

    dataset = create_dataset(
        [image_record],
        tmp_path,
    )

    working_dataset = WorkingDataset(dataset)

    config = DatasetConfig(
        blur_threshold=60.0,
    )

    result = BlurAnalyzer().analyze(
        working_dataset=working_dataset,
        config=config,
    )

    assert result.analyzer == "blur"
    assert result.images_checked == 1
    assert result.issues_found == 0


def test_blur_analyzer_handles_unreadable_image(
    tmp_path,
):

    image_path = tmp_path / "corrupted.jpg"

    image_path.write_bytes(
        b"this is not an image"
    )

    image_record = create_image_record(
        image_path,
        "corrupted.jpg",
    )

    dataset = create_dataset(
        [image_record],
        tmp_path,
    )

    working_dataset = WorkingDataset(dataset)

    config = DatasetConfig(
        blur_threshold=60.0,
    )

    result = BlurAnalyzer().analyze(
        working_dataset=working_dataset,
        config=config,
    )

    assert result.analyzer == "blur"
    assert result.images_checked == 1
    assert result.issues_found == 0