from PIL import Image

from app.analyzers.base import BaseAnalyzer
from app.core.working_dataset import WorkingDataset
from app.models import AnalysisResult, DatasetConfig, Finding


class CorruptionAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "corruption"

    def analyze(
        self,
        working_dataset: WorkingDataset,
        config: DatasetConfig,
    ) -> AnalysisResult:

        findings = []

        images_checked = working_dataset.total_images

        for image in working_dataset.images:

            try:
                with Image.open(image.path) as img:
                    img.verify()

            except Exception as error:

                findings.append(
                    Finding(
                        image_id=image.id,
                        issue_type="corruption",
                        severity="high",
                        reason=f"Image could not be verified: {error}",
                    )
                )

        return AnalysisResult(
            analyzer=self.name,
            images_checked=images_checked,
            findings=findings,
        )