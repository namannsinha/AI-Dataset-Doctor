import hashlib
from pathlib import Path


def calculate_file_hash(
    file_path: str,
    chunk_size: int = 8192,
) -> str:
    """
    Calculate the SHA-256 hash of a file.

    The file is read in chunks so that large files
    do not need to be loaded entirely into memory.
    """

    hasher = hashlib.sha256()

    with Path(file_path).open("rb") as file:

        while chunk := file.read(chunk_size):
            hasher.update(chunk)

    return hasher.hexdigest()