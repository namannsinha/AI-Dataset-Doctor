from pathlib import Path
import shutil

from app.core.working_dataset import WorkingDataset


class CleanDatasetManager:

    def __init__(
        self,
        output_root: str,
    ):
        self.output_root = Path(output_root)

        self.clean_root = (
            self.output_root / "Clean"
        )

        self.clean_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def export(
        self,
        working_dataset: WorkingDataset,
    ) -> None:

        for image in working_dataset.iter_images():

            source_path = Path(image.path)

            if not source_path.exists():
                raise FileNotFoundError(
                    f"Image file not found: {source_path}"
                )

            destination = (
                self.clean_root
                / image.original_path
            )

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                str(source_path),
                str(destination),
            )