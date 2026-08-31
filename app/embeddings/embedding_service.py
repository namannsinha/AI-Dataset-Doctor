from pathlib import Path

from PIL import Image
from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(
        self,
        model_name: str = "clip-ViT-B-16",
    ):
        self.model = SentenceTransformer(
            model_name
        )

    def generate_embeddings(
        self,
        image_paths: list[str],
    ):

        images = []
        valid_paths = []

        # -----------------------------------------
        # 1. Load images
        # -----------------------------------------

        for image_path in image_paths:

            path = Path(image_path)

            if not path.exists():

                print(
                    f"Image not found: {image_path}"
                )

                continue

            try:

                with Image.open(path) as image:

                    image = image.convert("RGB")

                    # Keep a copy after closing
                    # the source image.
                    images.append(image.copy())
                    valid_paths.append(image_path)

            except Exception as exc:

                print(
                    f"Unable to load image "
                    f"{image_path}: {exc}"
                )

        # -----------------------------------------
        # 2. Handle empty batch
        # -----------------------------------------

        if not images:
            return [], []

        # -----------------------------------------
        # 3. Generate embeddings for entire batch
        # -----------------------------------------

        try:

            embeddings = self.model.encode(
                images,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

        except Exception as exc:

            raise ValueError(
                "Unable to generate embeddings "
                "for image batch."
            ) from exc

        return embeddings, valid_paths