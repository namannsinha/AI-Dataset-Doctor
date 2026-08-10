from app.models import Dataset, ImageRecord


class WorkingDataset:

    def __init__(self, dataset: Dataset):
        self.dataset = dataset

        self._active_images = {
            image.id: image
            for image in dataset.images
        }

    @property
    def images(self) -> list[ImageRecord]:
        """
        Return the images currently active in the dataset.
        """
        return list(self._active_images.values())

    @property
    def total_images(self) -> int:
        """
        Number of images currently active.
        """
        return len(self._active_images)

    @property
    def original_total_images(self) -> int:
        """
        Number of images in the original dataset.
        """
        return len(self.dataset.images)

    def remove_images(self, image_ids: set[str]) -> None:
        """
        Remove images from the working dataset.

        This does NOT modify the original Dataset.
        """

        for image_id in image_ids:
            self._active_images.pop(image_id, None)

    def contains(self, image_id: str) -> bool:
        """
        Check whether an image is still active.
        """
        return image_id in self._active_images

    def get_image(self, image_id: str) -> ImageRecord | None:
        """
        Return an active image by ID.
        """
        return self._active_images.get(image_id)