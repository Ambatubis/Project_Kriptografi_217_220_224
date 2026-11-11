import os
import pytest
from PIL import Image
from steganography import lsb
from crypto.errors import CryptoError, DecryptionError

KEY = os.urandom(32)


def make_png(path, size=(100, 100)):
    Image.frombytes("RGB", size, os.urandom(size[0] * size[1] * 3)).save(path)
    return str(path)


def test_embed_extract(tmp_path):
    cover, out = make_png(tmp_path / "c.png"), str(tmp_path / "s.png")
    lsb.embed(cover, "Pesan tersembunyi 😀", KEY, out)
    assert lsb.extract(out, KEY) == "Pesan tersembunyi 😀"


def test_wrong_key(tmp_path):
    cover, out = make_png(tmp_path / "c.png"), str(tmp_path / "s.png")
    lsb.embed(cover, "rahasia", KEY, out)
    with pytest.raises(DecryptionError):
        lsb.extract(out, os.urandom(32))


def test_too_large(tmp_path):
    cover = make_png(tmp_path / "c.png", (10, 10))
    with pytest.raises(CryptoError):
        lsb.embed(cover, "x" * 500, KEY, str(tmp_path / "s.png"))


def test_clean_image_has_no_message(tmp_path):
    with pytest.raises(CryptoError):
        lsb.extract(make_png(tmp_path / "c.png"), KEY)


def test_only_png(tmp_path):
    p = tmp_path / "a.jpg"
    p.write_bytes(b"x")
    with pytest.raises(CryptoError):
        lsb.extract(str(p), KEY)
