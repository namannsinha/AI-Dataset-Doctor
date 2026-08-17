from pathlib import Path

import numpy as np


class EmbeddingStore:

    def __init__(
        self,
        output_root: str,
    ):
        self.root = (
            Path(output_root)
            / "embeddings"
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.embedding_path = (
            self.root / "embeddings.npy"
        )

        self.metadata_path = (
            self.root / "metadata.npz"
        )

    def append(
        self,
        embeddings: np.ndarray,
        image_ids: list[str],
        labels: list[str | None],
    ) -> None:

        if len(embeddings) != len(image_ids):
            raise ValueError(
                "Number of embeddings must match "
                "number of image IDs."
            )

        if len(image_ids) != len(labels):
            raise ValueError(
                "Number of image IDs must match "
                "number of labels."
            )

        # -----------------------------------------
        # First batch
        # -----------------------------------------

        if not self.embedding_path.exists():

            np.save(
                self.embedding_path,
                embeddings,
            )

            np.savez(
                self.metadata_path,
                image_ids=np.array(
                    image_ids,
                    dtype=str,
                ),
                labels=np.array(
                    [
                        label
                        if label is not None
                        else ""
                        for label in labels
                    ],
                    dtype=str,
                ),
            )

            return

        # -----------------------------------------
        # Existing data
        # -----------------------------------------

        existing_embeddings = np.load(
            self.embedding_path
        )

        metadata = np.load(
            self.metadata_path
        )

        existing_ids = metadata[
            "image_ids"
        ].tolist()

        existing_labels = metadata[
            "labels"
        ].tolist()

        # -----------------------------------------
        # Append embeddings
        # -----------------------------------------

        combined_embeddings = np.concatenate(
            [
                existing_embeddings,
                embeddings,
            ],
            axis=0,
        )

        # -----------------------------------------
        # Append metadata
        # -----------------------------------------

        combined_ids = (
            existing_ids
            + image_ids
        )

        combined_labels = (
            existing_labels
            + [
                label
                if label is not None
                else ""
                for label in labels
            ]
        )

        # -----------------------------------------
        # Rewrite store
        # -----------------------------------------

        np.save(
            self.embedding_path,
            combined_embeddings,
        )

        np.savez(
            self.metadata_path,
            image_ids=np.array(
                combined_ids,
                dtype=str,
            ),
            labels=np.array(
                combined_labels,
                dtype=str,
            ),
        )

    def load(self):

        if not self.embedding_path.exists():
            raise FileNotFoundError(
                "Embedding store does not exist."
            )

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                "Embedding metadata does not exist."
            )

        embeddings = np.load(
            self.embedding_path
        )

        metadata = np.load(
            self.metadata_path
        )

        image_ids = metadata[
            "image_ids"
        ].tolist()

        labels = metadata[
            "labels"
        ].tolist()

        labels = [
            label if label else None
            for label in labels
        ]

        return (
            embeddings,
            image_ids,
            labels,
        )

    def clear(self) -> None:

        if self.embedding_path.exists():
            self.embedding_path.unlink()

        if self.metadata_path.exists():
            self.metadata_path.unlink()