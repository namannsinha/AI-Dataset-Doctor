from app.analyzers.duplicate import DuplicateAnalyzer
from app.models.hash_result import ImageHash


def test_duplicate_analyzer_detects_duplicate():

    analyzer = DuplicateAnalyzer()

    first_batch = [
        ImageHash(
            image_id="image1.jpg",
            file_hash="ABC",
        )
    ]

    second_batch = [
        ImageHash(
            image_id="image2.jpg",
            file_hash="ABC",
        )
    ]

    # First image becomes the original.
    findings1 = analyzer.process_hashes(
        first_batch
    )

    assert findings1 == []

    # Second image has the same hash.
    findings2 = analyzer.process_hashes(
        second_batch
    )

    assert len(findings2) == 1

    finding = findings2[0]

    assert finding.image_id == "image2.jpg"
    assert finding.issue_type == "duplicate"
    assert finding.severity == "medium"

    assert (
        finding.reason
        == "Exact duplicate of image1.jpg."
    )


def test_unique_images_are_not_duplicates():

    analyzer = DuplicateAnalyzer()

    results = [
        ImageHash(
            image_id="image1.jpg",
            file_hash="ABC",
        ),
        ImageHash(
            image_id="image2.jpg",
            file_hash="XYZ",
        ),
    ]

    findings = analyzer.process_hashes(
        results
    )

    assert findings == []


def test_multiple_duplicates():

    analyzer = DuplicateAnalyzer()

    analyzer.process_hashes(
        [
            ImageHash(
                image_id="original.jpg",
                file_hash="ABC",
            )
        ]
    )

    findings = analyzer.process_hashes(
        [
            ImageHash(
                image_id="copy1.jpg",
                file_hash="ABC",
            ),
            ImageHash(
                image_id="copy2.jpg",
                file_hash="ABC",
            ),
        ]
    )

    assert len(findings) == 2

    assert findings[0].image_id == "copy1.jpg"
    assert findings[1].image_id == "copy2.jpg"

    assert (
        findings[0].reason
        == "Exact duplicate of original.jpg."
    )

    assert (
        findings[1].reason
        == "Exact duplicate of original.jpg."
    )


def test_duplicates_across_batches():

    analyzer = DuplicateAnalyzer()

    # Batch 1
    findings1 = analyzer.process_hashes(
        [
            ImageHash(
                image_id="batch1/image.jpg",
                file_hash="ABC",
            )
        ]
    )

    assert findings1 == []

    # Batch 2
    findings2 = analyzer.process_hashes(
        [
            ImageHash(
                image_id="batch2/image.jpg",
                file_hash="ABC",
            )
        ]
    )

    assert len(findings2) == 1

    assert (
        findings2[0].image_id
        == "batch2/image.jpg"
    )