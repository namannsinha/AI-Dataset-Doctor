from app.core.working_dataset import WorkingDataset
from app.models import Dataset, DatasetType, ImageRecord


def create_dataset():
    images = [
        ImageRecord(
            id="image1.jpg",
            path="image1.jpg",
            original_path="image1.jpg",
            filename="image1.jpg",
            width=100,
            height=100,
            format="jpg",
            file_size=1000,
        ),
        ImageRecord(
            id="image2.jpg",
            path="image2.jpg",
            original_path="image2.jpg",
            filename="image2.jpg",
            width=100,
            height=100,
            format="jpg",
            file_size=1000,
        ),
        ImageRecord(
            id="image3.jpg",
            path="image3.jpg",
            original_path="image3.jpg",
            filename="image3.jpg",
            width=100,
            height=100,
            format="jpg",
            file_size=1000,
        ),
    ]

    return Dataset(
        dataset_id="test_dataset",
        name="Test Dataset",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path="test_dataset",
        images=images,
    )


def test_working_dataset_initialization():

    dataset = create_dataset()

    working_dataset = WorkingDataset(dataset)

    assert working_dataset.total_images == 3
    assert working_dataset.original_total_images == 3


def test_remove_images():

    dataset = create_dataset()

    working_dataset = WorkingDataset(dataset)

    working_dataset.remove_images({
        "image2.jpg"
    })

    assert working_dataset.total_images == 2

    assert working_dataset.contains("image1.jpg")
    assert not working_dataset.contains("image2.jpg")
    assert working_dataset.contains("image3.jpg")


def test_original_dataset_is_not_modified():

    dataset = create_dataset()

    working_dataset = WorkingDataset(dataset)

    working_dataset.remove_images({
        "image1.jpg",
        "image2.jpg",
    })

    assert working_dataset.total_images == 1

    # Original Dataset must remain untouched
    assert len(dataset.images) == 3