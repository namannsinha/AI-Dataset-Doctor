from app.core.batch_manager import BatchManager
from app.models import ImageRecord


def create_image_records(count: int) -> list[ImageRecord]:
    return [
        ImageRecord(
            id=f"image_{i}.jpg",
            path=f"/dataset/image_{i}.jpg",
            original_path=f"image_{i}.jpg",
            filename=f"image_{i}.jpg",
            width=100,
            height=100,
            format="jpg",
            file_size=1000,
        )
        for i in range(count)
    ]


def test_batch_manager_creates_correct_batches():

    images = create_image_records(250)

    batch_manager = BatchManager(
        images=images,
        batch_size=100,
    )

    batches = list(batch_manager)

    assert len(batches) == 3

    assert batches[0].size == 100
    assert batches[1].size == 100
    assert batches[2].size == 50


def test_batch_manager_preserves_image_order():

    images = create_image_records(5)

    batch_manager = BatchManager(
        images=images,
        batch_size=2,
    )

    batches = list(batch_manager)

    ids = [
        image.id
        for batch in batches
        for image in batch.images
    ]

    assert ids == [
        "image_0.jpg",
        "image_1.jpg",
        "image_2.jpg",
        "image_3.jpg",
        "image_4.jpg",
    ]


def test_batch_manager_rejects_invalid_batch_size():

    images = create_image_records(10)

    try:
        BatchManager(
            images=images,
            batch_size=0,
        )

        assert False

    except ValueError:
        assert True

def test_batch_manager_accepts_generator():

    images = create_image_records(5)

    image_generator = (
        image
        for image in images
    )

    manager = BatchManager(
        images=image_generator,
        batch_size=2,
    )

    batches = list(manager)

    assert len(batches) == 3

    assert batches[0].size == 2
    assert batches[1].size == 2
    assert batches[2].size == 1