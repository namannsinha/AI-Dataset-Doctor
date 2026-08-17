import hashlib


def calculate_file_hash(
    file_path: str,
    chunk_size: int = 1024 * 1024,
) -> str:
    """
    Calculate the SHA-256 hash of a file.

    The file is read in chunks so that large files
    do not need to be loaded completely into memory.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            chunk = file.read(chunk_size)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()