import numpy as np

from app.embeddings.embedding_store import EmbeddingStore


def test_embedding_store_save_and_load(
    tmp_path,
):

    # -----------------------------------------
    # Arrange
    # -----------------------------------------

    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )

    image_ids = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
    ]

    labels = [
        "cat",
        "dog",
        None,
    ]

    store = EmbeddingStore(
        output_root=str(tmp_path),
    )

    # -----------------------------------------
    # Act
    # -----------------------------------------

    store.append(
        embeddings=embeddings,
        image_ids=image_ids,
        labels=labels,
    )

    loaded_embeddings, loaded_ids, loaded_labels = (
        store.load()
    )

    # -----------------------------------------
    # Assert embeddings
    # -----------------------------------------

    assert np.array_equal(
        loaded_embeddings,
        embeddings,
    )

    # -----------------------------------------
    # Assert image IDs
    # -----------------------------------------

    assert loaded_ids == image_ids

    # -----------------------------------------
    # Assert labels
    # -----------------------------------------

    assert loaded_labels == labels


def test_embedding_store_creates_files(
    tmp_path,
):

    store = EmbeddingStore(
        output_root=str(tmp_path),
    )

    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
        ],
        dtype=np.float32,
    )

    store.append(
        embeddings=embeddings,
        image_ids=["image1.jpg"],
        labels=["cat"],
    )

    assert store.embedding_path.exists()
    assert store.metadata_path.exists()

def test_embedding_store_appends_batches(
    tmp_path,
):

    store = EmbeddingStore(
        output_root=str(tmp_path),
    )

    # First batch
    store.append(
        embeddings=np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float32,
        ),
        image_ids=[
            "image1.jpg",
            "image2.jpg",
        ],
        labels=[
            "cat",
            "dog",
        ],
    )

    # Second batch
    store.append(
        embeddings=np.array(
            [
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float32,
        ),
        image_ids=[
            "image3.jpg",
        ],
        labels=[
            None,
        ],
    )

    embeddings, image_ids, labels = (
        store.load()
    )

    assert embeddings.shape == (3, 3)

    assert image_ids == [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
    ]

    assert labels == [
        "cat",
        "dog",
        None,
    ]

def test_embedding_store_clear(
    tmp_path,
):

    store = EmbeddingStore(
        output_root=str(tmp_path),
    )

    store.append(
        embeddings=np.array(
            [
                [1.0, 0.0, 0.0],
            ],
            dtype=np.float32,
        ),
        image_ids=["image1.jpg"],
        labels=["cat"],
    )

    store.clear()

    assert not store.embedding_path.exists()
    assert not store.metadata_path.exists()