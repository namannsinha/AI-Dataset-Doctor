from app.core.hash_worker import hash_batch
from app.models.ImageBatch import ImageBatch
from app.models import ImageRecord


def test_hash_batch(tmp_path):

    file1 = tmp_path / "image1.jpg"
    file2 = tmp_path / "image2.jpg"

    file1.write_bytes(
        b"same image content"
    )

    file2.write_bytes(
        b"same image content"
    )

    image1 = ImageRecord(
        id="image1.jpg",
        path=str(file1),
        original_path="image1.jpg",
        filename="image1.jpg",
        width=100,
        height=100,
        format="jpg",
        file_size=file1.stat().st_size,
    )

    image2 = ImageRecord(
        id="image2.jpg",
        path=str(file2),
        original_path="image2.jpg",
        filename="image2.jpg",
        width=100,
        height=100,
        format="jpg",
        file_size=file2.stat().st_size,
    )

    batch = ImageBatch(
        batch_id=1,
        images=[
            image1,
            image2,
        ],
    )

    results = hash_batch(batch)

    assert len(results) == 2

    assert results[0].image_id == "image1.jpg"
    assert results[1].image_id == "image2.jpg"

    assert (
        results[0].file_hash
        == results[1].file_hash
    )