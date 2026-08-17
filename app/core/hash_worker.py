from app.models import ImageBatch
from app.models.hash_result import ImageHash
from app.utils.hashing import calculate_file_hash


def hash_batch(
    batch: ImageBatch,
) -> list[ImageHash]:

    results = []

    for image in batch.images:

        file_hash = calculate_file_hash(
            image.path
        )

        results.append(
            ImageHash(
                image_id=image.id,
                file_hash=file_hash,
            )
        )

    return results