from app.analyzers.base import BaseAnalyzer
from app.models import (
    AnalysisResult,
    DatasetConfig,
    Finding,
    ImageBatch,
)
from app.utils.blur import calculate_blur_score


class BlurAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "blur"

    def analyze(
        self,
        working_dataset: ImageBatch,
        config: DatasetConfig,
    ) -> AnalysisResult:

        findings = []

        for image in working_dataset.images:

            try:
                blur_score = calculate_blur_score(
                    image.path
                )

            except Exception:
                # Corrupted/unreadable images are handled
                # by the CorruptionAnalyzer.
                continue

            if blur_score < config.blur_threshold:

                findings.append(
                    Finding(
                        image_id=image.id,
                        issue_type="blur",
                        severity="medium",
                        reason=(
                            f"Image blur score is "
                            f"{blur_score:.2f}, which is below "
                            f"the minimum threshold of "
                            f"{config.blur_threshold:.2f}."
                        ),
                    )
                )

        return AnalysisResult(
            analyzer=self.name,
            images_checked=len(working_dataset.images),
            findings=findings,
        )