from collections.abc import Iterator
from app.sources.folder_source import FolderDatasetSource
from app.models import Dataset, ImageRecord


class WorkingDataset:

    def __init__(
        self,
        dataset: Dataset,
        image_source=None,
    ):
        self.dataset = dataset

        if image_source is not None:
            self.image_source = image_source

        elif dataset.has_streaming_source:
            self.image_source = FolderDatasetSource(
                dataset.root_path
            )

        else:
            self.image_source = None

        self._active_images = {
            image.id: image
            for image in dataset.images
        }

        self._removed_image_ids: set[str] = set()

    @property
    def images(self) -> list[ImageRecord]:
        """
        Return the currently active images.

        This is the existing list-based interface.
        """
        return list(self._active_images.values())

    def iter_images(self) -> Iterator[ImageRecord]:
        """
        Stream active images from the dataset source.

        If no source is configured, fall back to the
        existing in-memory images.
        """

        if self.image_source is None:

            for image in self._active_images.values():

                if image.id not in self._removed_image_ids:
                    yield image

            return

        for image in self.image_source.iter_records():

            if image.id in self._removed_image_ids:
                continue

            yield image

    @property
    def total_images(self) -> int:
        """
        Number of currently active images.
        """
        return len(self._active_images)

    @property
    def original_total_images(self) -> int:
        """
        Number of images in the original dataset.
        """
        return len(self.dataset.images)

    def remove_images(
        self,
        image_ids: set[str],
    ) -> None:
        """
        Remove images from the working dataset.

        This updates the working state but does not
        modify the original Dataset.
        """

        for image_id in image_ids:

            self._active_images.pop(
                image_id,
                None,
            )

            self._removed_image_ids.add(
                image_id
            )

    def contains(
        self,
        image_id: str,
    ) -> bool:
        """
        Check whether an image is still active.
        """

        return image_id in self._active_images

    def get_image(
        self,
        image_id: str,
    ) -> ImageRecord | None:
        """
        Return an active image by ID.
        """

        return self._active_images.get(image_id)