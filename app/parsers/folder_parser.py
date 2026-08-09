from pathlib import Path

from PIL import Image

from app.models import Dataset, ImageRecord


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tiff",
    ".tif",
}

SPLIT_NAMES = {
    "train",
    "test",
    "val",
    "validation",
}


class FolderParser:

    def parse(self, folder_path: str) -> Dataset:
        root = Path(folder_path)

        if not root.exists():
            raise FileNotFoundError(f"Dataset folder not found: {folder_path}")

        if not root.is_dir():
            raise ValueError(f"Expected a directory: {folder_path}")

        image_files = self._find_images(root)

        if not image_files:
            raise ValueError("No supported image files found in dataset.")

        source_format = self._detect_format(root, image_files)

        images = [
            self._create_image_record(
                root=root,
                image_path=image_path,
                source_format=source_format,
            )
            for image_path in image_files
        ]

        classes = sorted(
            {
                image.label
                for image in images
                if image.label is not None
            }
        )

        splits = sorted(
            {
                image.split
                for image in images
                if image.split is not None
            }
        )

        return Dataset(
            dataset_id=root.name,
            name=root.name,
            source_format=source_format,
            root_path=str(root.resolve()),
            images=images,
            classes=classes,
            splits=splits,
        )

    def _find_images(self, root: Path) -> list[Path]:
        return sorted(
            path
            for path in root.rglob("*")
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )

    def _detect_format(
        self,
        root: Path,
        image_files: list[Path],
    ) -> str:

        relative_parts = [
            image_path.relative_to(root).parts
            for image_path in image_files
        ]

        # Case 1:
        # dataset/train/cat/image.jpg
        # dataset/test/dog/image.jpg
        for parts in relative_parts:
            if parts and parts[0].lower() in SPLIT_NAMES:
                return "structured_folder"

        # Case 2:
        # dataset/cat/image.jpg
        # dataset/dog/image.jpg
        for parts in relative_parts:
            if len(parts) >= 2:
                return "class_folder"

        # Case 3:
        # dataset/image.jpg
        return "flat_folder"

    def _create_image_record(
        self,
        root: Path,
        image_path: Path,
        source_format: str,
    ) -> ImageRecord:

        relative_path = image_path.relative_to(root)
        parts = relative_path.parts

        label = None
        split = None

        if source_format == "structured_folder":
            if len(parts) >= 3:
                split = parts[0]
                label = parts[1]

        elif source_format == "class_folder":
            if len(parts) >= 2:
                label = parts[0]

        width = None
        height = None
        image_format = image_path.suffix.lower().replace(".", "")

        try:
            with Image.open(image_path) as image:
                width, height = image.size

                if image.format:
                    image_format = image.format.lower()

        except Exception:
            # The image may be corrupted.
            # We intentionally don't fail here.
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