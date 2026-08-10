from PIL import Image

from app.models import DatasetType
from app.parsers.folder_parser import FolderParser


def create_test_image(path):
    path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", (100, 100))
    image.save(path)


def test_parse_train_test_dataset(tmp_path):

    create_test_image(
        tmp_path / "train" / "cat" / "cat1.jpg"
    )

    create_test_image(
        tmp_path / "train" / "dog" / "dog1.jpg"
    )

    create_test_image(
        tmp_path / "test" / "cat" / "cat2.jpg"
    )

    create_test_image(
        tmp_path / "test" / "dog" / "dog2.jpg"
    )

    parser = FolderParser()

    dataset = parser.parse(str(tmp_path))

    assert dataset.dataset_type == DatasetType.TRAIN_TEST

    assert dataset.source_format == "folder"

    assert len(dataset.images) == 4

    assert "cat" in dataset.classes
    assert "dog" in dataset.classes

    assert "train" in dataset.splits
    assert "test" in dataset.splits

def test_parse_class_separated_dataset(tmp_path):

    create_test_image(
        tmp_path / "cat" / "cat1.jpg"
    )

    create_test_image(
        tmp_path / "cat" / "cat2.jpg"
    )

    create_test_image(
        tmp_path / "dog" / "dog1.jpg"
    )

    parser = FolderParser()

    dataset = parser.parse(str(tmp_path))

    assert dataset.dataset_type == DatasetType.CLASS_SEPARATED

    assert dataset.source_format == "folder"

    assert len(dataset.images) == 3

    assert "cat" in dataset.classes
    assert "dog" in dataset.classes

    assert dataset.splits == []

    for image in dataset.images:
        assert image.label is not None
        assert image.split is None

def test_parse_flat_dataset(tmp_path):

    create_test_image(
        tmp_path / "image1.jpg"
    )

    create_test_image(
        tmp_path / "image2.jpg"
    )

    create_test_image(
        tmp_path / "image3.jpg"
    )

    parser = FolderParser()

    dataset = parser.parse(str(tmp_path))

    assert dataset.dataset_type == DatasetType.FLAT

    assert dataset.source_format == "folder"

    assert len(dataset.images) == 3

    assert dataset.classes == []

    assert dataset.splits == []

    for image in dataset.images:
        assert image.label is None
        assert image.split is None