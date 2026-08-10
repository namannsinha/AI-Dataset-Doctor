from pathlib import Path

from PIL import Image

from app.models import Dataset, DatasetType, ImageRecord


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

        # 1. Validate input folder
        if not root.exists():
            raise FileNotFoundError(
                f"Dataset folder not found: {folder_path}"
            )

        if not root.is_dir():
            raise ValueError(
                f"Expected a directory: {folder_path}"
            )

        # 2. Find all supported images
        image_files = self._find_images(root)

        if not image_files:
            raise ValueError(
                "No supported image files found in dataset."
            )

        # 3. Detect dataset structure
        dataset_type = self._detect_dataset_type(
            root,
            image_files,
        )

        # 4. Convert every image into an ImageRecord
        images = [
            self._create_image_record(
                root=root,
                image_path=image_path,
                dataset_type=dataset_type,
            )
            for image_path in image_files
        ]

        # 5. Extract classes
        classes = sorted(
            {
                image.label
                for image in images
                if image.label is not None
            }
        )

        # 6. Extract splits
        splits = sorted(
            {
                image.split
                for image in images
                if image.split is not None
            }
        )

        # 7. Create the common Dataset object
        return Dataset(
            dataset_id=root.name,
            name=root.name,
            dataset_type=dataset_type,
            source_format="folder",
            root_path=str(root.resolve()),
            images=images,
            classes=classes,
            splits=splits,
        )

    def _find_images(self, root: Path) -> list[Path]:
        """
        Find all supported image files recursively.
        """

        return sorted(
            path
            for path in root.rglob("*")
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )

    def _detect_dataset_type(
        self,
        root: Path,
        image_files: list[Path],
    ) -> DatasetType:
        """
        Determine whether the dataset is:

        - TRAIN_TEST
        - CLASS_SEPARATED
        - FLAT
        """

        relative_parts = [
            image_path.relative_to(root).parts
            for image_path in image_files
        ]

        # Example:
        # train/cat/image.jpg
        # test/dog/image.jpg
        for parts in relative_parts:
            if (
                parts
                and parts[0].lower() in SPLIT_NAMES
            ):
                return DatasetType.TRAIN_TEST

        # Example:
        # cat/image.jpg
        # dog/image.jpg
        for parts in relative_parts:
            if len(parts) >= 2:
                return DatasetType.CLASS_SEPARATED

        # Example:
        # image.jpg
        # image2.jpg
        return DatasetType.FLAT

    def _create_image_record(
        self,
        root: Path,
        image_path: Path,
        dataset_type: DatasetType,
    ) -> ImageRecord:
        """
        Convert one image file into an ImageRecord.
        """

        relative_path = image_path.relative_to(root)
        parts = relative_path.parts

        label = None
        split = None

        # -------------------------
        # TRAIN / TEST DATASET
        # -------------------------
        #
        # train/cat/image.jpg
        # test/dog/image.jpg
        #
        if dataset_type == DatasetType.TRAIN_TEST:

            if len(parts) >= 3:
                split = parts[0]
                label = parts[1]

        # -------------------------
        # CLASS-SEPARATED DATASET
        # -------------------------
        #
        # cat/image.jpg
        # dog/image.jpg
        #
        elif dataset_type == DatasetType.CLASS_SEPARATED:

            if len(parts) >= 2:
                label = parts[0]

        # -------------------------
        # FLAT DATASET
        # -------------------------
        #
        # image.jpg
        #
        # label and split remain None.

        width = None
        height = None

        # We can determine the format from the extension
        # even if the image itself is corrupted.
        image_format = (
            image_path.suffix
            .lower()
            .replace(".", "")
        )

        try:
            with Image.open(image_path) as image:

                width, height = image.size

                # Pillow may know the actual image format.
                if image.format:
                    image_format = image.format.lower()

        except Exception:
            # Do NOT remove the image here.
            #
            # A corrupted image is still represented by
            # ImageRecord so that the Corruption Analyzer
            # can detect and quarantine it later.
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