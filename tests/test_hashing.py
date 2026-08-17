from app.utils.hashing import calculate_file_hash


def test_identical_files_have_same_hash(tmp_path):

    file1 = tmp_path / "image1.jpg"
    file2 = tmp_path / "image2.jpg"

    content = b"same file content"

    file1.write_bytes(content)
    file2.write_bytes(content)

    hash1 = calculate_file_hash(str(file1))
    hash2 = calculate_file_hash(str(file2))

    assert hash1 == hash2


def test_different_files_have_different_hash(tmp_path):

    file1 = tmp_path / "image1.jpg"
    file2 = tmp_path / "image2.jpg"

    file1.write_bytes(b"content A")
    file2.write_bytes(b"content B")

    hash1 = calculate_file_hash(str(file1))
    hash2 = calculate_file_hash(str(file2))

    assert hash1 != hash2


def test_filename_does_not_affect_hash(tmp_path):

    file1 = tmp_path / "cat.jpg"
    file2 = tmp_path / "completely_different_name.jpg"

    content = b"same content"

    file1.write_bytes(content)
    file2.write_bytes(content)

    assert (
        calculate_file_hash(str(file1))
        == calculate_file_hash(str(file2))
    )

from app.utils.hashing import calculate_file_hash


def test_same_content_produces_same_hash(tmp_path):

    file1 = tmp_path / "image1.jpg"
    file2 = tmp_path / "image2.jpg"

    content = b"same image content"

    file1.write_bytes(content)
    file2.write_bytes(content)

    hash1 = calculate_file_hash(
        str(file1)
    )

    hash2 = calculate_file_hash(
        str(file2)
    )

    assert hash1 == hash2


def test_different_content_produces_different_hash(
    tmp_path,
):

    file1 = tmp_path / "image1.jpg"
    file2 = tmp_path / "image2.jpg"

    file1.write_bytes(
        b"image content one"
    )

    file2.write_bytes(
        b"image content two"
    )

    hash1 = calculate_file_hash(
        str(file1)
    )

    hash2 = calculate_file_hash(
        str(file2)
    )

    assert hash1 != hash2


def test_filename_does_not_affect_hash(
    tmp_path,
):

    file1 = tmp_path / "cat.jpg"
    file2 = tmp_path / "dog.jpg"

    content = b"identical file contents"

    file1.write_bytes(content)
    file2.write_bytes(content)

    assert calculate_file_hash(
        str(file1)
    ) == calculate_file_hash(
        str(file2)
    )


def test_large_file_is_hashed_correctly(
    tmp_path,
):

    file_path = tmp_path / "large.jpg"

    content = b"A" * (3 * 1024 * 1024)

    file_path.write_bytes(content)

    actual_hash = calculate_file_hash(
        str(file_path)
    )

    expected_hash = __import__(
        "hashlib"
    ).sha256(content).hexdigest()

    assert actual_hash == expected_hash