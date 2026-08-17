from collections.abc import Iterator
from pathlib import Path

from PIL import Image

from app.models.image import ImageRecord
from app.models import DatasetType
from app.models.dataset_metadata import DatasetMetadata


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tiff",
    ".tif",
}


class FolderDatasetSource:

    def __init__(self, root_path: str):

        self.root = Path(root_path)

        if not self.root.exists():
            raise FileNotFoundError(
                f"Dataset folder not found: {root_path}"
            )

        if not self.root.is_dir():
            raise ValueError(
                f"Expected a directory: {root_path}"
            )

    def iter_records(self) -> Iterator[ImageRecord]:

        for path in self.root.rglob("*"):

            if not path.is_file():
                continue

            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            yield self._create_image_record(path)

    def _create_image_record(
        self,
        image_path: Path,
    ) -> ImageRecord:

        relative_path = image_path.relative_to(
            self.root
        )

        parts = relative_path.parts

        label = None
        split = None

        # -------------------------
        # Detect train/test structure
        # -------------------------

        split_names = {
            "train",
            "test",
            "val",
            "validation",
        }

        if parts and parts[0].lower() in split_names:

            split = parts[0]

            if len(parts) >= 3:
                label = parts[1]

        # -------------------------
        # Detect class-folder structure
        # -------------------------

        elif len(parts) >= 2:

            label = parts[0]

        # -------------------------
        # Image metadata
        # -------------------------

        width = None
        height = None

        image_format = (
            image_path.suffix
            .lower()
            .replace(".", "")
        )

        try:

            with Image.open(image_path) as image:

                width, height = image.size

                if image.format:
                    image_format = (
                        image.format.lower()
                    )

        except Exception:
            # Corrupted images are allowed to
            # reach the analyzers.
            pass

        return ImageRecord(
            id=str(relative_path),
            path=str(image_path),
            original_path=str(relative_path),
            filename=image_path.name,
            label=label,
            split=split,
            width=width,
            height=height,
            format=image_format,
            file_size=image_path.stat().st_size,
        )

    def discover_metadata(self) -> DatasetMetadata:

        classes = set()
        splits = set()
        image_count = 0

        relative_parts_list = []

        for path in self.root.rglob("*"):

            if not path.is_file():
                continue

            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            image_count += 1

            relative_parts = path.relative_to(
                self.root
            ).parts

            relative_parts_list.append(
                relative_parts
            )

        # -------------------------
        # Detect dataset type
        # -------------------------

        dataset_type = DatasetType.FLAT

        split_names = {
            "train",
            "test",
            "val",
            "validation",
        }

        for parts in relative_parts_list:

            if (
                parts
                and parts[0].lower() in split_names
            ):
                dataset_type = DatasetType.TRAIN_TEST
                break

        else:

            for parts in relative_parts_list:

                if len(parts) >= 2:
                    dataset_type = DatasetType.CLASS_SEPARATED
                    break

        # -------------------------
        # Extract classes and splits
        # -------------------------

        for parts in relative_parts_list:

            if not parts:
                continue

            first = parts[0]

            if first.lower() in split_names:

                splits.add(first)

                if len(parts) >= 2:
                    classes.add(parts[1])

            elif len(parts) >= 2:

                classes.add(parts[0])

        return DatasetMetadata(
            dataset_type=dataset_type,
            classes=sorted(classes),
            splits=sorted(splits),
            image_count=image_count,
        )