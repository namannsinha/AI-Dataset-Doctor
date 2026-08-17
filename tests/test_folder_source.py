from app.sources.folder_source import FolderDatasetSource
from app.core.batch_manager import BatchManager
from app.models import DatasetType
from app.sources.folder_source import FolderDatasetSource

def test_folder_source_streams_records(tmp_path):

    dataset_root = tmp_path / "dataset"

    image1 = dataset_root / "cat" / "cat1.jpg"
    image2 = dataset_root / "dog" / "dog1.jpg"

    image1.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image2.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image1.write_bytes(b"test image 1")
    image2.write_bytes(b"test image 2")

    source = FolderDatasetSource(
        str(dataset_root)
    )

    records = source.iter_records()

    first = next(records)
    second = next(records)

    assert first.id == "cat/cat1.jpg"
    assert second.id == "dog/dog1.jpg"

def test_folder_source_is_lazy(tmp_path):

    dataset_root = tmp_path / "dataset"

    image_path = dataset_root / "image.jpg"

    image_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_path.write_bytes(b"test image")

    source = FolderDatasetSource(
        str(dataset_root)
    )

    records = source.iter_records()

    assert hasattr(records, "__next__")

    record = next(records)

    assert record.id == "image.jpg"

def test_folder_source_to_batch_manager(tmp_path):

    dataset_root = tmp_path / "dataset"

    image_paths = [
        dataset_root / "cat" / "cat1.jpg",
        dataset_root / "cat" / "cat2.jpg",
        dataset_root / "dog" / "dog1.jpg",
        dataset_root / "dog" / "dog2.jpg",
        dataset_root / "dog" / "dog3.jpg",
    ]

    for path in image_paths:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            b"test image"
        )

    source = FolderDatasetSource(
        str(dataset_root)
    )

    manager = BatchManager(
        images=source.iter_records(),
        batch_size=2,
    )

    batches = list(manager)

    assert len(batches) == 3

    assert batches[0].size == 2
    assert batches[1].size == 2
    assert batches[2].size == 1

    all_images = [
        image
        for batch in batches
        for image in batch.images
    ]

    assert len(all_images) == 5

def test_folder_source_discovers_metadata(tmp_path):

    dataset_root = tmp_path / "dataset"

    paths = [
        dataset_root / "train" / "cat" / "cat1.jpg",
        dataset_root / "train" / "dog" / "dog1.jpg",
        dataset_root / "test" / "cat" / "cat2.jpg",
    ]

    for path in paths:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            b"test image"
        )

    source = FolderDatasetSource(
        str(dataset_root)
    )

    metadata = source.discover_metadata()

    assert metadata.dataset_type == DatasetType.TRAIN_TEST

    assert metadata.classes == [
        "cat",
        "dog",
    ]

    assert metadata.splits == [
        "test",
        "train",
    ]

    assert metadata.image_count == 3