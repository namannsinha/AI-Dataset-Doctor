from PIL import Image
from app.models.ImageBatch import ImageBatch
from app.analyzers.corruption import CorruptionAnalyzer
from app.models import (
    DatasetConfig,
    ImageRecord,
)


def test_corruption_analyzer_detects_corrupted_image(
    tmp_path,
):

    valid_path = tmp_path / "valid.jpg"
    corrupted_path = tmp_path / "corrupted.jpg"

    # -------------------------
    # Create valid image
    # -------------------------

    image = Image.new(
        "RGB",
        (100, 100),
    )

    image.save(valid_path)

    # -------------------------
    # Create corrupted file
    # -------------------------

    corrupted_path.write_bytes(
        b"this is not a valid image"
    )

    # -------------------------
    # Create ImageRecords
    # -------------------------

    valid_record = ImageRecord(
        id="valid.jpg",
        path=str(valid_path),
        original_path="valid.jpg",
        filename="valid.jpg",
        width=100,
        height=100,
        format="jpg",
        file_size=valid_path.stat().st_size,
    )

    corrupted_record = ImageRecord(
        id="corrupted.jpg",
        path=str(corrupted_path),
        original_path="corrupted.jpg",
        filename="corrupted.jpg",
        width=None,
        height=None,
        format="jpg",
        file_size=corrupted_path.stat().st_size,
    )

    batch = ImageBatch(
        batch_id=1,
        images=[
            valid_record,
            corrupted_record,
        ],
    )

    analyzer = CorruptionAnalyzer()

    result = analyzer.analyze(
        working_dataset=batch,
        config=DatasetConfig(),
    )

    # -------------------------
    # Assertions
    # -------------------------

    assert result.images_checked == 2

    assert result.issues_found == 1

    assert result.findings[0].image_id == "corrupted.jpg"

    assert result.findings[0].issue_type == "corrupted"

    assert result.findings[0].severity == "high"