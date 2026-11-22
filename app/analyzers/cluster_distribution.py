
from pathlib import Path

from app.analyzers.base import BaseAnalyzer
from app.models import AnalysisResult, DatasetConfig
from app.analyzers.class_distribution import ClassDistributionAnalyzer


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tiff",
    ".tif",
}


class ClusterDistributionAnalyzer(BaseAnalyzer):

    @property
    def name(self) -> str:
        return "cluster_distribution"

    def analyze(
        self,
        working_dataset,
        config: DatasetConfig,
    ) -> AnalysisResult:
        raise NotImplementedError(
            "Use analyze_cluster_folders() instead."
        )

    def analyze_cluster_folders(
        self,
        cluster_output_dir: Path,
        config: DatasetConfig,
    ) -> AnalysisResult:

        cluster_output_dir = Path(cluster_output_dir)

        if not cluster_output_dir.is_dir():
            return AnalysisResult(
                analyzer=self.name,
                images_checked=0,
                findings=[],
                statistics={
                    "status": "not_applicable",
                    "message": "Cluster output directory not found.",
                },
            )

        cluster_counts = {}
        empty_clusters = []

        cluster_dirs = sorted(
            path
            for path in cluster_output_dir.iterdir()
            if path.is_dir()
            and path.name.startswith("cluster_")
        )

        for cluster_dir in cluster_dirs:

            image_count = sum(
                1
                for path in cluster_dir.rglob("*")
                if path.is_file()
                and path.suffix.lower() in SUPPORTED_EXTENSIONS
            )

            if image_count == 0:
                empty_clusters.append(cluster_dir.name)
                continue

            cluster_counts[cluster_dir.name] = image_count

        if not cluster_counts:
            return AnalysisResult(
                analyzer=self.name,
                images_checked=0,
                findings=[],
                statistics={
                    "status": "not_applicable",
                    "message": "No images found in cluster folders.",
                    "empty_clusters": empty_clusters,
                },
            )

        total_images = sum(cluster_counts.values())

        percentages = {
            cluster: round(
                count / total_images * 100,
                2,
            )
            for cluster, count in cluster_counts.items()
        }

        largest_cluster = max(
            cluster_counts,
            key=cluster_counts.get,
        )

        smallest_cluster = min(
            cluster_counts,
            key=cluster_counts.get,
        )

        imbalance_ratio = round(
            cluster_counts[largest_cluster]
            / cluster_counts[smallest_cluster],
            2,
        )

        underrepresented_clusters = [
            cluster
            for cluster, percentage in percentages.items()
            if percentage < config.min_cluster_percentage
        ]

        statistics = {
            "status": "completed",
            "source": "exported_cluster_folders",
            "total_images": total_images,
            "total_clusters": len(cluster_counts),
            "cluster_counts": cluster_counts,
            "cluster_percentages": percentages,
            "largest_cluster": largest_cluster,
            "smallest_cluster": smallest_cluster,
            "imbalance_ratio": imbalance_ratio,
            "underrepresented_clusters": underrepresented_clusters,
            "empty_clusters": empty_clusters,
        }

        return AnalysisResult(
            analyzer=self.name,
            images_checked=total_images,
            findings=[],
            statistics=statistics,
        )
