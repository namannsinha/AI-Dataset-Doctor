from app.analyzers.base import BaseAnalyzer
from app.models import (
    AnalysisResult,
    DatasetConfig,
    Finding,
    ImageBatch,
)


class ResolutionAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "resolution"

    def analyze(
        self,
        working_dataset: ImageBatch,
        config: DatasetConfig,
    ) -> AnalysisResult:

        findings = []

        for image in working_dataset.images:

            if image.width is None or image.height is None:
                continue

            if (
                image.width < config.min_width
                or image.height < config.min_height
            ):

                findings.append(
                    Finding(
                        image_id=image.id,
                        issue_type="low_resolution",
                        severity="medium",
                        reason=(
                            f"Image resolution is "
                            f"{image.width}x{image.height}. "
                            f"Minimum required resolution is "
                            f"{config.min_width}x"
                            f"{config.min_height}."
                        ),
                    )
                )

        return AnalysisResult(
            analyzer=self.name,
            images_checked=len(working_dataset.images),
            findings=findings,
        )