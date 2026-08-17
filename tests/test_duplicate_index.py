from app.core.duplicate_index import DuplicateIndex


def test_duplicate_index_stores_hashes():

    index = DuplicateIndex()

    index.add(
        image_id="image1.jpg",
        file_hash="ABC",
    )

    index.add(
        image_id="image2.jpg",
        file_hash="XYZ",
    )

    assert index.contains_hash("ABC")
    assert index.contains_hash("XYZ")


def test_duplicate_index_detects_duplicate_hash():

    index = DuplicateIndex()

    index.add(
        image_id="image1.jpg",
        file_hash="ABC",
    )

    index.add(
        image_id="image2.jpg",
        file_hash="ABC",
    )

    duplicates = index.get_duplicates()

    assert duplicates == {
        "ABC": [
            "image1.jpg",
            "image2.jpg",
        ]
    }


def test_unique_hashes_are_not_duplicates():

    index = DuplicateIndex()

    index.add(
        image_id="image1.jpg",
        file_hash="ABC",
    )

    index.add(
        image_id="image2.jpg",
        file_hash="XYZ",
    )

    assert index.get_duplicates() == {}


def test_duplicate_index_works_across_batches():

    index = DuplicateIndex()

    # Batch 1
    index.add(
        image_id="batch1/image1.jpg",
        file_hash="ABC",
    )

    # Batch 2
    index.add(
        image_id="batch2/image2.jpg",
        file_hash="ABC",
    )

    duplicates = index.get_duplicates()

    assert duplicates["ABC"] == [
        "batch1/image1.jpg",
        "batch2/image2.jpg",
    ]