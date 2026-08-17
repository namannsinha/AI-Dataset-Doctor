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

    def generate_embedding(
        self,
        image_path: str,
    ):

        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        try:
            with Image.open(path) as image:

                image = image.convert("RGB")

                embedding = self.model.encode(
                    image,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                )

        except Exception as e:

            raise ValueError(
                f"Unable to generate embedding "
                f"for image: {image_path}"
            ) from e

        return embedding