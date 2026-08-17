from collections import defaultdict


class DuplicateIndex:

    def __init__(self):
        self._hash_to_images: dict[str, list[str]] = defaultdict(list)

    def add(
        self,
        image_id: str,
        file_hash: str,
    ) -> None:
        """
        Add an image and its hash to the index.
        """

        self._hash_to_images[file_hash].append(
            image_id
        )

    def get_duplicates(
        self,
    ) -> dict[str, list[str]]:
        """
        Return only hashes that belong to
        more than one image.
        """

        return {
            file_hash: image_ids
            for file_hash, image_ids
            in self._hash_to_images.items()
            if len(image_ids) > 1
        }

    def contains_hash(
        self,
        file_hash: str,
    ) -> bool:
        """
        Check whether a hash already exists.
        """

        return file_hash in self._hash_to_images

    def get_images(
        self,
        file_hash: str,
    ) -> list[str]:
        """
        Return all image IDs associated
        with a hash.
        """

        return list(
            self._hash_to_images.get(
                file_hash,
                []
            )
        )