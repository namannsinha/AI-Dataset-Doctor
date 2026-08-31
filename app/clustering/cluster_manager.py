from pathlib import Path
import shutil

from app.core.working_dataset import WorkingDataset


class ClusterManager:

    def __init__(
        self,
        output_root: str,
    ):
        self.output_root = Path(output_root)

    def create_clusters(
        self,
        working_dataset: WorkingDataset,
        cluster_assignments: dict[str, int],
        num_clusters: int,
        output_dir: str = "clusters",
    ) -> Path:
        """
        Create separated folders containing copies of
        images according to their cluster assignments.

        Example:

        clusters/
        ├── cluster_0/
        ├── cluster_1/
        ├── cluster_2/
        └── ...

        The original dataset is not modified.
        """

        if num_clusters < 1:
            raise ValueError(
                "num_clusters must be at least 1."
            )

        cluster_root = (
            self.output_root / output_dir
        )

        # -----------------------------------------
        # 1. Create cluster root directory
        # -----------------------------------------

        cluster_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -----------------------------------------
        # 2. Create all cluster directories
        # -----------------------------------------

        for cluster_number in range(
            num_clusters
        ):

            cluster_dir = (
                cluster_root
                / f"cluster_{cluster_number}"
            )

            cluster_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

        # -----------------------------------------
        # 3. Copy images into their clusters
        # -----------------------------------------

        copied_count = 0

        for image_id, cluster_number in (
            cluster_assignments.items()
        ):

            image = working_dataset.get_image(
                image_id
            )

            if image is None:
                print(
                    f"Warning: image '{image_id}' "
                    f"not found in working dataset."
                )
                continue

            source_path = Path(
                image.path
            )

            if not source_path.exists():

                print(
                    f"Warning: image file not found: "
                    f"{source_path}"
                )

                continue

            cluster_dir = (
                cluster_root
                / f"cluster_{cluster_number}"
            )

            destination_path = (
                cluster_dir
                / image.filename
            )

            shutil.copy2(
                source_path,
                destination_path,
            )

            copied_count += 1

        print(
            f"Clustered {copied_count} images "
            f"into {num_clusters} clusters."
        )

        print(
            f"Cluster output: {cluster_root}"
        )

        return cluster_root