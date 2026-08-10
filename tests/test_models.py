from app.models import Dataset, DatasetType, ImageRecord


def test_image_record():
    image = ImageRecord(
        id="img_001",
        path="train/dog/dog_001.jpg",
        original_path="train/dog/dog_001.jpg",
        filename="dog_001.jpg",
        label="dog",
        split="train",
        width=512,
        height=512,
        format="jpg",
        file_size=123456,
    )

    assert image.filename == "dog_001.jpg"
    assert image.label == "dog"
    assert image.width == 512


def test_dataset():
    image = ImageRecord(
        id="img_001",
        path="train/dog/dog_001.jpg",
        original_path="train/dog/dog_001.jpg",
        filename="dog_001.jpg",
        label="dog",
        split="train",
        width=512,
        height=512,
        format="jpg",
        file_size=123456,
    )

    dataset = Dataset(
        dataset_id="dataset_001",
        name="Cats vs Dogs",
        dataset_type=DatasetType.TRAIN_TEST,
        source_format="folder",
        root_path="data/sample_dataset",
        images=[image],
        classes=["cat", "dog"],
        splits=["train", "test"],
    )

    assert dataset.name == "Cats vs Dogs"
    assert len(dataset.images) == 1
    assert "dog" in dataset.classes