
import numpy as np
from sklearn.cluster import KMeans

from app.analyzers.base import BaseAnalyzer
from app.models import (
    AnalysisResult,
    DatasetConfig,
    Finding,
)


class ClusteringAnalyzer(BaseAnalyzer):

    def __init__(self):
        self.cluster_assignments: dict[str, int] = {}

    @property
    def name(self) -> str:
        return "clustering"

    def analyze(
        self,
        working_dataset,
        config: DatasetConfig,
    ) -> AnalysisResult:
        return AnalysisResult(
            analyzer=self.name,
            images_checked=0,
            findings=[],
        )

    def process_embeddings(
        self,
        embeddings: np.ndarray,
        image_ids: list[str],
        config: DatasetConfig,
    ) -> AnalysisResult:

        self.cluster_assignments = {}

        if not config.enable_clustering:
            return AnalysisResult(
                analyzer=self.name,
                images_checked=len(image_ids),
                findings=[],
            )

        if len(embeddings) == 0:
            return AnalysisResult(
                analyzer=self.name,
                images_checked=0,
                findings=[],
            )

        if len(embeddings) != len(image_ids):
            raise ValueError(
                "Number of embeddings must match "
                "number of image IDs."
            )

        num_clusters = config.num_clusters

        if num_clusters < 1:
            raise ValueError(
                "num_clusters must be at least 1."
            )

        if num_clusters > len(embeddings):
            raise ValueError(
                "num_clusters cannot be greater "
                "than the number of images."
            )

        clustering = KMeans(
            n_clusters=num_clusters,
            random_state=42,
            n_init=10,
        )

        cluster_labels = clustering.fit_predict(embeddings)

        # Map each image ID to its cluster number.
        cluster_assignments = {
            image_id: int(cluster_label)
            for image_id, cluster_label
            in zip(image_ids, cluster_labels)
        }

        # Keep assignments available for cluster export.
        self.cluster_assignments = cluster_assignments

        # Calculate each image's distance from its assigned cluster center.
        distances = clustering.transform(embeddings)

        assigned_distances = distances[
            np.arange(len(embeddings)),
            cluster_labels,
        ]

        # Flag images unusually far from their cluster center.
        distance_threshold = float(
            np.mean(assigned_distances)
            + 2 * np.std(assigned_distances)
        )

        findings = []

        for index, distance in enumerate(assigned_distances):
            if distance <= distance_threshold:
                continue

            findings.append(
                Finding(
                    image_id=image_ids[index],
                    issue_type="visual_outlier",
                    severity="medium",
                    reason=(
                        "Image is unusually far from "
                        "the center of its visual cluster."
                    ),
                    value=float(distance),
                    threshold=distance_threshold,
                )
            )

        return AnalysisResult(
            analyzer=self.name,
            images_checked=len(image_ids),
            findings=findings,
            cluster_assignments=cluster_assignments,
        )
