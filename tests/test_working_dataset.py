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

def test_working_dataset_streams_from_source(tmp_path):

    dataset_root = tmp_path / "dataset"

    image_paths = [
        dataset_root / "cat" / "cat1.jpg",
        dataset_root / "dog" / "dog1.jpg",
    ]

    for path in image_paths:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            b"test image"
        )

    from app.sources.folder_source import (
        FolderDatasetSource,
    )

    source = FolderDatasetSource(
        str(dataset_root)
    )

    # Dataset object can remain empty here.
    # The records will come from the source.
    dataset = Dataset(
        dataset_id="stream_test",
        name="Stream Test",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(dataset_root),
        images=[],
    )

    working_dataset = WorkingDataset(
        dataset=dataset,
        image_source=source,
    )

    records = list(
        working_dataset.iter_images()
    )

    assert len(records) == 2

    assert {
        image.id
        for image in records
    } == {
        "cat/cat1.jpg",
        "dog/dog1.jpg",
    }

def test_working_dataset_stream_skips_removed_images(
    tmp_path,
):

    dataset_root = tmp_path / "dataset"

    image_paths = [
        dataset_root / "image1.jpg",
        dataset_root / "image2.jpg",
    ]

    for path in image_paths:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            b"test image"
        )

    from app.sources.folder_source import (
        FolderDatasetSource,
    )

    source = FolderDatasetSource(
        str(dataset_root)
    )

    dataset = Dataset(
        dataset_id="stream_test",
        name="Stream Test",
        dataset_type=DatasetType.FLAT,
        source_format="folder",
        root_path=str(dataset_root),
        images=[],
    )

    working_dataset = WorkingDataset(
        dataset=dataset,
        image_source=source,
    )

    working_dataset.remove_images(
        {"image1.jpg"}
    )

    records = list(
        working_dataset.iter_images()
    )

    assert len(records) == 1

    assert records[0].id == "image2.jpg"

def test_working_dataset_auto_creates_streaming_source(
    tmp_path,
):

    dataset_root = tmp_path / "dataset"

    paths = [
        dataset_root / "cat" / "cat1.jpg",
        dataset_root / "dog" / "dog1.jpg",
    ]

    for path in paths:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            b"test image"
        )

    dataset = Dataset(
        dataset_id="stream_dataset",
        name="Stream Dataset",
        dataset_type=DatasetType.CLASS_SEPARATED,
        source_format="folder",
        root_path=str(dataset_root),
        images=[],
        classes=["cat", "dog"],
        splits=[],
        has_streaming_source=True,
    )

    working_dataset = WorkingDataset(
        dataset
    )

    records = list(
        working_dataset.iter_images()
    )

    assert len(records) == 2

    assert {
        image.id
        for image in records
    } == {
        "cat/cat1.jpg",
        "dog/dog1.jpg",
    }