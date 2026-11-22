
from collections import defaultdict

from app.analyzers.base import BaseAnalyzer
from app.core.working_dataset import WorkingDataset
from app.models import AnalysisResult, DatasetConfig


class ClassDistributionAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "class_distribution"

    def analyze(
        self,
        working_dataset: WorkingDataset,
        config: DatasetConfig,
    ) -> AnalysisResult:

        images = list(working_dataset.iter_images())

        # Separate images by split.
        split_images = defaultdict(list)

        for image in images:
            split_name = image.split or "all"
            split_images[split_name].append(image)

        statistics = {
            "total_images": len(images),
            "labeled_images": sum(
                1 for image in images
                if image.label is not None
            ),
            "unlabeled_images": sum(
                1 for image in images
                if image.label is None
            ),
            "splits": {},
        }

        # No labels: class distribution is not applicable.
        if not any(image.label is not None for image in images):
            statistics["status"] = "not_applicable"
            statistics["message"] = (
                "No class labels were found in the dataset."
            )

            return AnalysisResult(
                analyzer=self.name,
                images_checked=len(images),
                findings=[],
                statistics=statistics,
            )

        statistics["status"] = "completed"

        for split_name, split_records in split_images.items():

            class_counts = {}

            for image in split_records:
                if image.label is None:
                    continue

                class_counts[image.label] = (
                    class_counts.get(image.label, 0) + 1
                )

            labeled_count = sum(class_counts.values())

            if labeled_count == 0:
                continue

            class_percentages = {
                label: round(
                    count / labeled_count * 100,
                    2,
                )
                for label, count in class_counts.items()
            }

            largest_count = max(class_counts.values())
            smallest_count = min(class_counts.values())

            imbalance_ratio = round(
                largest_count / smallest_count,
                2,
            )

            underrepresented_classes = [
                label
                for label, percentage in class_percentages.items()
                if percentage < config.min_class_percentage
            ]

            statistics["splits"][split_name] = {
                "total_images": len(split_records),
                "labeled_images": labeled_count,
                "unlabeled_images": (
                    len(split_records) - labeled_count
                ),
                "class_counts": class_counts,
                "class_percentages": class_percentages,
                "largest_class": max(
                    class_counts,
                    key=class_counts.get,
                ),
                "smallest_class": min(
                    class_counts,
                    key=class_counts.get,
                ),
                "imbalance_ratio": imbalance_ratio,
                "underrepresented_classes": (
                    underrepresented_classes
                ),
            }

        return AnalysisResult(
            analyzer=self.name,
            images_checked=len(images),
            findings=[],
            statistics=statistics,
        )
