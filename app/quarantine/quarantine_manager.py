
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
        self.output_root = Path(output_root).resolve()
        self.working_dataset = working_dataset

        self.input_root = Path(
            working_dataset.dataset.root_path
        ).resolve()

        self.quarantine_root = (
            self.output_root / "Quarantine"
        ).resolve()

        # Quarantine must never be inside the input dataset.
        if (
            self.quarantine_root == self.input_root
            or self.input_root in self.quarantine_root.parents
        ):
            raise ValueError(
                "Quarantine directory must be outside "
                "the input dataset directory."
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

        # 2. Resolve and validate the source path.
        source_path = Path(image.path).resolve()

        if not source_path.is_file():
            raise FileNotFoundError(
                f"Image file not found: {source_path}"
            )

        if not source_path.is_relative_to(self.input_root):
            raise ValueError(
                "Refusing to quarantine an image outside "
                f"the input dataset: {source_path}"
            )

        # 3. Resolve the destination and prevent path traversal.
        relative_path = Path(image.original_path)

        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(
                "Invalid image relative path: "
                f"{image.original_path}"
            )

        category = analyzer_name.lower()

        if (
            not category
            or category in {".", ".."}
            or Path(category).name != category
        ):
            raise ValueError(
                f"Invalid analyzer name: {analyzer_name}"
            )

        destination = (
            self.quarantine_root
            / category
            / relative_path
        ).resolve()

        if (
            destination == source_path
            or destination.is_relative_to(self.input_root)
        ):
            raise ValueError(
                "Refusing to write quarantine output "
                "inside the input dataset."
            )

        # 4. Create destination directories.
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # 5. Copy, never move, the original image.
        shutil.copy2(
            source_path,
            destination,
        )

        # 6. Exclude the image from the active working dataset.
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
