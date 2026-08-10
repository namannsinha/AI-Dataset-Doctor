from pathlib import Path
import shutil

from app.core.working_dataset import WorkingDataset
from app.models import Finding, QuarantineRecord


class QuarantineManager:

    def __init__(
        self,
        output_root: str,
        working_dataset: WorkingDataset,
    ):
        self.output_root = Path(output_root)
        self.working_dataset = working_dataset

        self.quarantine_root = (
            self.output_root / "Quarantine"
        )

        self.quarantine_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def quarantine(
        self,
        finding: Finding,
        analyzer_name: str,
    ) -> QuarantineRecord:

        # 1. Find the image in the active dataset.
        image = self.working_dataset.get_image(
            finding.image_id
        )

        if image is None:
            raise ValueError(
                "Image is not active in working dataset: "
                f"{finding.image_id}"
            )

        # 2. Locate the actual file.
        source_path = Path(image.path)

        if not source_path.exists():
            raise FileNotFoundError(
                f"Image file not found: {source_path}"
            )

        # 3. Create analyzer-specific quarantine path.
        category = analyzer_name.lower()

        destination = (
            self.quarantine_root
            / category
            / image.original_path
        )

        # 4. Create destination directories.
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # 5. Move the physical file.
        shutil.move(
            str(source_path),
            str(destination),
        )

        # 6. Remove the image from the working dataset.
        self.working_dataset.remove_images(
            {image.id}
        )

        # 7. Record what happened.
        return QuarantineRecord(
            image_id=image.id,
            original_path=image.original_path,
            quarantine_path=str(destination),
            reason=finding.reason,
            analyzer=analyzer_name,
        )