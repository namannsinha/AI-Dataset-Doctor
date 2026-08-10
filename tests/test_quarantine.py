from app.models import QuarantineRecord


def test_quarantine_record():

    record = QuarantineRecord(
        image_id="train/cat/cat17.jpg",
        original_path="train/cat/cat17.jpg",
        quarantine_path=(
            "output/Quarantine/"
            "blur/train/cat/cat17.jpg"
        ),
        reason="Image is too blurry",
        analyzer="BlurAnalyzer",
    )

    assert record.image_id == "train/cat/cat17.jpg"

    assert (
        record.original_path
        == "train/cat/cat17.jpg"
    )

    assert (
        record.quarantine_path
        == (
            "output/Quarantine/"
            "blur/train/cat/cat17.jpg"
        )
    )

    assert record.reason == "Image is too blurry"

    assert record.analyzer == "BlurAnalyzer"