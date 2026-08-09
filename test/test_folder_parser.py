from app.parsers.folder_parser import FolderParser


def test_parse_structured_dataset():

    parser = FolderParser()

    dataset = parser.parse("data/sample_dataset")

    assert dataset.source_format == "structured_folder"

    assert len(dataset.images) == 5

    assert "cat" in dataset.classes
    assert "dog" in dataset.classes

    assert "train" in dataset.splits
    assert "test" in dataset.splits