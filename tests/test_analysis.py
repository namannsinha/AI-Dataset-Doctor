from app.models import AnalysisResult, Finding


def test_analysis_result():

    findings = [
        Finding(
            image_id="image1.jpg",
            issue_type="blur",
            severity="medium",
            reason="Blur score below threshold",
            value=42.0,
            threshold=60.0,
        ),
        Finding(
            image_id="image2.jpg",
            issue_type="blur",
            severity="high",
            reason="Blur score below threshold",
            value=20.0,
            threshold=60.0,
        ),
    ]

    result = AnalysisResult(
        analyzer="blur",
        images_checked=100,
        findings=findings,
    )

    assert result.analyzer == "blur"
    assert result.images_checked == 100
    assert len(result.findings) == 2
    assert result.issues_found == 2