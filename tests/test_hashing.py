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