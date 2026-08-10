from app.analyzers.base import BaseAnalyzer
from app.core.working_dataset import WorkingDataset
from app.models import (
    AnalysisResult,
    DatasetConfig,
    Finding,
)


class ResolutionAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "resolution"

    def analyze(
        self,
        working_dataset: WorkingDataset,
        config: DatasetConfig,
    ) -> AnalysisResult:

        findings = []

        for image in working_dataset.images:

            # Metadata should normally already be
            # available from FolderParser.
            if image.width is None or image.height is None:

                findings.append(
                    Finding(
                        image_id=image.id,
                        issue_type="resolution",
                        severity="high",
                        reason=(
                            "Image dimensions could not "
                            "be determined."
                        ),
                    )
                )

                continue

            width = image.width
            height = image.height

            if (
                width < config.min_width
                or height < config.min_height
            ):

                findings.append(
                    Finding(
                        image_id=image.id,
                        issue_type="resolution",
                        severity="medium",
                        reason=(
                            f"Image resolution is "
                            f"{width}x{height}, "
                            f"below minimum "
                            f"{config.min_width}x"
                            f"{config.min_height}."
                        ),
                    )
                )

        return AnalysisResult(
            analyzer=self.name,
            images_checked=working_dataset.total_images,
            findings=findings,
        )