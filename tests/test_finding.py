from app.models import Finding


def test_finding():

    finding = Finding(
        image_id="train/cat/cat17.jpg",
        issue_type="blur",
        severity="medium",
        reason="Blur score is below configured threshold",
        value=42.7,
        threshold=60.0,
    )

    assert finding.image_id == "train/cat/cat17.jpg"
    assert finding.issue_type == "blur"
    assert finding.severity == "medium"
    assert finding.value == 42.7
    assert finding.threshold == 60.0