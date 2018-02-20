import tempfile

from Crypto.Hash import SHA256

from syncr_backend.file_metadata import hash_file


def test_hash_file():
    with tempfile.TemporaryFile() as f:
        f.write(b'x\11' * 1001)
        f.seek(0)

        h_out = hash_file(f)
        h_expected_builder = SHA256.new()
        expected_data = b'x\11' * 1001
        h_expected_builder.update(expected_data)
        h_expected = h_expected_builder.digest()

        assert len(h_out) == 1
        assert h_out[0] == h_expected
