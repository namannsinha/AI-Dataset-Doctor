import numpy as np
import pytest

from app.analyzers.label_validation import (
    LabelValidationAnalyzer,
)
from app.models import DatasetConfig


def create_config(
    enable_label_validation=True,
    label_similarity_threshold=0.75,
    label_margin=0.03,
):
    return DatasetConfig(
        enable_label_validation=enable_label_validation,
        label_similarity_threshold=label_similarity_threshold,
        label_margin=label_margin,
    )


def create_test_embeddings():
    """
    Create two clearly separated classes.

    Class A:
        [1, 0]
        [0.95, 0.05]
        [0.90, 0.10]

    Class B:
        [0, 1]
        [0.05, 0.95]
        [0.10, 0.90]
    """

    return np.array(
        [
            [1.0, 0.0],
            [0.95, 0.05],
            [0.90, 0.10],
            [0.0, 1.0],
            [0.05, 0.95],
            [0.10, 0.90],
        ],
        dtype=np.float32,
    )


def create_test_image_ids():
    return [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
        "image4.jpg",
        "image5.jpg",
        "image6.jpg",
    ]


def create_test_labels():
    return [
        "cat",
        "cat",
        "cat",
        "dog",
        "dog",
        "dog",
    ]


def test_label_validation_analyzer_name():

    analyzer = LabelValidationAnalyzer()

    assert analyzer.name == "label_validation"


def test_label_validation_disabled():

    analyzer = LabelValidationAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = create_test_image_ids()

    labels = create_test_labels()

    config = create_config(
        enable_label_validation=False,
    )

    result = analyzer.process_embeddings(
        embeddings=embeddings,
        image_ids=image_ids,
        labels=labels,
        config=config,
    )

    assert result.analyzer == "label_validation"

    assert result.images_checked == 6

    assert result.findings == []


def test_label_validation_empty_embeddings():

    analyzer = LabelValidationAnalyzer()

    embeddings = np.empty(
        (0, 2),
        dtype=np.float32,
    )

    image_ids = []

    labels = []

    config = create_config()

    result = analyzer.process_embeddings(
        embeddings=embeddings,
        image_ids=image_ids,
        labels=labels,
        config=config,
    )

    assert result.analyzer == "label_validation"

    assert result.images_checked == 0

    assert result.findings == []


def test_label_validation_requires_matching_lengths():

    analyzer = LabelValidationAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = create_test_image_ids()

    labels = [
        "cat",
        "cat",
        "cat",
    ]

    config = create_config()

    with pytest.raises(ValueError):

        analyzer.process_embeddings(
            embeddings=embeddings,
            image_ids=image_ids,
            labels=labels,
            config=config,
        )


def test_label_validation_requires_multiple_classes():

    analyzer = LabelValidationAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = create_test_image_ids()

    labels = [
        "cat",
        "cat",
        "cat",
        "cat",
        "cat",
        "cat",
    ]

    config = create_config()

    result = analyzer.process_embeddings(
        embeddings=embeddings,
        image_ids=image_ids,
        labels=labels,
        config=config,
    )

    assert result.images_checked == 6

    assert result.findings == []


def test_label_validation_ignores_unlabeled_images():

    analyzer = LabelValidationAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = create_test_image_ids()

    labels = [
        "cat",
        "cat",
        None,
        "dog",
        "dog",
        "dog",
    ]

    config = create_config()

    result = analyzer.process_embeddings(
        embeddings=embeddings,
        image_ids=image_ids,
        labels=labels,
        config=config,
    )

    assert result.images_checked == 6

    for finding in result.findings:

        assert finding.image_id != "image3.jpg"


def test_label_validation_detects_wrong_label():

    analyzer = LabelValidationAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = create_test_image_ids()

    # image3 has a dog-like embedding
    # but is incorrectly labeled as cat.
    embeddings[2] = np.array(
        [0.05, 0.95],
        dtype=np.float32,
    )

    labels = [
        "cat",
        "cat",
        "cat",
        "dog",
        "dog",
        "dog",
    ]

    config = create_config(
        label_margin=0.03,
    )

    result = analyzer.process_embeddings(
        embeddings=embeddings,
        image_ids=image_ids,
        labels=labels,
        config=config,
    )

    wrong_label_findings = [
        finding
        for finding in result.findings
        if finding.issue_type == "wrong_label"
    ]

    assert len(wrong_label_findings) >= 1

    assert any(
        finding.image_id == "image3.jpg"
        for finding in wrong_label_findings
    )


def test_label_validation_does_not_flag_correct_labels():

    analyzer = LabelValidationAnalyzer()

    embeddings = create_test_embeddings()

    image_ids = create_test_image_ids()

    labels = create_test_labels()

    config = create_config(
        label_similarity_threshold=0.50,
        label_margin=0.03,
    )

    result = analyzer.process_embeddings(
        embeddings=embeddings,
        image_ids=image_ids,
        labels=labels,
        config=config,
    )

    wrong_label_findings = [
        finding
        for finding in result.findings
        if finding.issue_type == "wrong_label"
    ]

    assert wrong_label_findings == []


def test_label_validation_detects_low_similarity():

    analyzer = LabelValidationAnalyzer()

    embeddings = np.array(
        [
            [1.0, 0.0],
            [0.99, 0.01],
            [0.0, 1.0],
            [0.01, 0.99],

            # Suspicious cat image
            [0.707, 0.707],
        ],
        dtype=np.float32,
    )

    image_ids = [
        "cat1.jpg",
        "cat2.jpg",
        "dog1.jpg",
        "dog2.jpg",
        "cat3.jpg",
    ]

    labels = [
        "cat",
        "cat",
        "dog",
        "dog",
        "cat",
    ]

    config = create_config(
        label_similarity_threshold=0.80,
        label_margin=0.50,
    )

    result = analyzer.process_embeddings(
        embeddings=embeddings,
        image_ids=image_ids,
        labels=labels,
        config=config,
    )

    suspicious_findings = [
        finding
        for finding in result.findings
        if finding.issue_type == "suspicious_label"
    ]

    assert len(suspicious_findings) >= 1

    assert any(
        finding.image_id == "cat3.jpg"
        for finding in suspicious_findings
    )