from collections import defaultdict

from app.analyzers.base import BaseAnalyzer
from app.core.working_dataset import WorkingDataset
from app.models import (
    AnalysisResult,
    DatasetConfig,
    Finding,
)
from app.utils.hashing import calculate_file_hash


class DuplicateAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "duplicate"

    def analyze(
        self,
        working_dataset: WorkingDataset,
        config: DatasetConfig,
    ) -> AnalysisResult:

        findings = []

        hash_groups = defaultdict(list)

        # --------------------------------
        # 1. Calculate hash for each image
        # --------------------------------

        for image in working_dataset.images:

            file_hash = calculate_file_hash(
                image.path
            )

            hash_groups[file_hash].append(
                image
            )

        # --------------------------------
        # 2. Find duplicate groups
        # --------------------------------

        for images in hash_groups.values():

            if len(images) <= 1:
                continue

            # Keep the first image.
            retained_image = images[0]

            # Every remaining image is a duplicate.
            for duplicate_image in images[1:]:

                findings.append(
                    Finding(
                        image_id=duplicate_image.id,
                        issue_type="duplicate",
                        severity="medium",
                        reason=(
                            "Exact duplicate of "
                            f"{retained_image.id}"
                        ),
                    )
                )

        return AnalysisResult(
            analyzer=self.name,
            images_checked=working_dataset.total_images,
            findings=findings,
        )