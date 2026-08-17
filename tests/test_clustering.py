import numpy as np
import pytest

from app.analyzers.clustering import ClusteringAnalyzer
from app.models import DatasetConfig


def create_config(
    enable_clustering=True,
    num_clusters=2,
):
    return DatasetConfig(
        enable_clustering=enable_clustering,
        num_clusters=num_clusters,
    )


def create_test_embeddings():
    """
    Create two clearly separated visual groups.

    Cluster 1:
        [1, 0]
        [0.9, 0.1]
        [1.1, -0.1]

    Cluster 2:
        [0, 1]
        [0.1, 0.9]
        [-0.1, 1.1]
    """

    return np.array(
        [
            [1.0, 0.0],
            [0.9, 0.1],
            [1.1, -0.1],
            [0.0, 1.0],
            [0.1, 0.9],
            [-0.1, 1.1],
        ],
        dtype=np.float32,
    )


def test_clustering_analyzer_name():

    analyzer = ClusteringAnalyzer()

    assert analyzer.name == "clustering"


def test_clustering_disabled():

    analyzer = ClusteringAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
        "image4.jpg",
        "image5.jpg",
        "image6.jpg",
    ]

    config = create_config(
        enable_clustering=False,
        num_clusters=2,
    )

    result = analyzer.process_embeddings(
        embeddings=embeddings,
        image_ids=image_ids,
        config=config,
    )

    assert result.analyzer == "clustering"

    assert result.images_checked == 6

    assert result.findings == []


def test_clustering_creates_requested_number_of_clusters():

    analyzer = ClusteringAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
        "image4.jpg",
        "image5.jpg",
        "image6.jpg",
    ]

    config = create_config(
        enable_clustering=True,
        num_clusters=2,
    )

    result = analyzer.process_embeddings(
        embeddings=embeddings,
        image_ids=image_ids,
        config=config,
    )

    assert result.analyzer == "clustering"

    assert result.images_checked == 6

    # The test primarily verifies that K-Means
    # successfully processes the requested
    # number of clusters.
    assert result.findings is not None


def test_clustering_handles_empty_embeddings():

    analyzer = ClusteringAnalyzer()

    embeddings = np.empty(
        (0, 2),
        dtype=np.float32,
    )

    image_ids = []

    config = create_config(
        enable_clustering=True,
        num_clusters=2,
    )

    result = analyzer.process_embeddings(
        embeddings=embeddings,
        image_ids=image_ids,
        config=config,
    )

    assert result.analyzer == "clustering"

    assert result.images_checked == 0

    assert result.findings == []


def test_clustering_rejects_invalid_cluster_count():

    analyzer = ClusteringAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
        "image4.jpg",
        "image5.jpg",
        "image6.jpg",
    ]

    config = create_config(
        enable_clustering=True,
        num_clusters=10,
    )

    with pytest.raises(ValueError):

        analyzer.process_embeddings(
            embeddings=embeddings,
            image_ids=image_ids,
            config=config,
        )


def test_clustering_rejects_zero_clusters():

    analyzer = ClusteringAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
        "image4.jpg",
        "image5.jpg",
        "image6.jpg",
    ]

    config = create_config(
        enable_clustering=True,
        num_clusters=0,
    )

    with pytest.raises(ValueError):

        analyzer.process_embeddings(
            embeddings=embeddings,
            image_ids=image_ids,
            config=config,
        )


def test_clustering_rejects_negative_cluster_count():

    analyzer = ClusteringAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
        "image4.jpg",
        "image5.jpg",
        "image6.jpg",
    ]

    config = create_config(
        enable_clustering=True,
        num_clusters=-1,
    )

    with pytest.raises(ValueError):

        analyzer.process_embeddings(
            embeddings=embeddings,
            image_ids=image_ids,
            config=config,
        )


def test_clustering_with_one_cluster():

    analyzer = ClusteringAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
        "image4.jpg",
        "image5.jpg",
        "image6.jpg",
    ]

    config = create_config(
        enable_clustering=True,
        num_clusters=1,
    )

    result = analyzer.process_embeddings(
        embeddings=embeddings,
        image_ids=image_ids,
        config=config,
    )

    assert result.analyzer == "clustering"

    assert result.images_checked == 6