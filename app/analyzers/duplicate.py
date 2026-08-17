from app.analyzers.base import BaseAnalyzer
from app.core.duplicate_index import DuplicateIndex
from app.models import (
    AnalysisResult,
    DatasetConfig,
    Finding,
    ImageBatch,
)
from app.models.hash_result import ImageHash


class DuplicateAnalyzer(BaseAnalyzer):

    def __init__(self):
        self.index = DuplicateIndex()

    @property
    def name(self) -> str:
        return "duplicate"

    def analyze(
        self,
        working_dataset: ImageBatch,
        config: DatasetConfig,
    ) -> AnalysisResult:

        # Normal analyzer contract.
        #
        # Actual duplicate detection is performed
        # through process_hashes().
        return AnalysisResult(
            analyzer=self.name,
            images_checked=len(
                working_dataset.images
            ),
            findings=[],
        )

    def process_hashes(
        self,
        hash_results: list[ImageHash],
    ) -> list[Finding]:

        findings = []

        for image_hash in hash_results:

            existing_images = self.index.get_images(
                image_hash.file_hash
            )

            self.index.add(
                image_id=image_hash.image_id,
                file_hash=image_hash.file_hash,
            )

            if existing_images:

                original_image = existing_images[0]

                findings.append(
                    Finding(
                        image_id=image_hash.image_id,
                        issue_type="duplicate",
                        severity="medium",
                        reason=(
                            f"Exact duplicate of "
                            f"{original_image}."
                        ),
                    )
                )

        return findings