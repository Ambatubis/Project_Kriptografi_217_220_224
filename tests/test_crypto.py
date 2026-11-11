import os
import pytest
from crypto import aes_gcm, vigenere
from crypto.super_text import encrypt_text, decrypt_text
from crypto.fernet_file import encrypt_file, decrypt_file
from crypto.errors import DecryptionError, CryptoError

KEY = os.urandom(32)


def test_vigenere_known_vector():
    assert vigenere.encrypt("ATTACKATDAWN", "LEMON") == "LXFOPVEFRNHR"
    assert vigenere.decrypt("LXFOPVEFRNHR", "LEMON") == "ATTACKATDAWN"


def test_vigenere_keeps_case_and_symbols():
    t = "Halo, Dunia! 123"
    assert vigenere.decrypt(vigenere.encrypt(t, "kunci"), "kunci") == t


def test_vigenere_invalid_key():
    with pytest.raises(CryptoError):
        vigenere.encrypt("abc", "123")


def test_aes_roundtrip_and_unique_nonce():
    c1, c2 = aes_gcm.encrypt(KEY, b"data"), aes_gcm.encrypt(KEY, b"data")
    assert c1 != c2 and aes_gcm.decrypt(KEY, c1) == b"data"


def test_aes_tamper_detected():
    c = bytearray(aes_gcm.encrypt(KEY, b"data"))
    c[-1] ^= 1
    with pytest.raises(DecryptionError):
        aes_gcm.decrypt(KEY, bytes(c))


def test_aes_wrong_key():
    with pytest.raises(DecryptionError):
        aes_gcm.decrypt(os.urandom(32), aes_gcm.encrypt(KEY, b"x"))


def test_super_text_roundtrip():
    c = encrypt_text("Pesan rahasia ÄÖ 😀", "KUNCI", KEY)
    assert decrypt_text(c, "KUNCI", KEY) == "Pesan rahasia ÄÖ 😀"


def test_super_text_wrong_vigenere_key_gives_garbage_not_original():
    c = encrypt_text("Pesan rahasia", "KUNCI", KEY)
    assert decrypt_text(c, "SALAH", KEY) != "Pesan rahasia"


def test_super_text_tamper_and_bad_format():
    c = encrypt_text("Pesan", "KUNCI", KEY)
    with pytest.raises(DecryptionError):
        decrypt_text(c[:-6] + "AAAA==", "KUNCI", KEY)
    with pytest.raises(DecryptionError):
        decrypt_text("bukan base64!!", "KUNCI", KEY)


def test_fernet_file_roundtrip_keeps_original(tmp_path):
    src = tmp_path / "dok.txt"
    src.write_bytes(b"isi file rahasia")
    enc, sha = encrypt_file(str(src), KEY)
    assert enc.name == "dok.txt.svault" and src.exists() and len(sha) == 64
    assert enc.read_bytes() != b"isi file rahasia"
    (tmp_path / "out").mkdir()
    out = decrypt_file(str(enc), KEY, out_dir=str(tmp_path / "out"))
    assert out.read_bytes() == b"isi file rahasia"


def test_fernet_wrong_key(tmp_path):
    src = tmp_path / "a.bin"
    src.write_bytes(b"x")
    enc, _ = encrypt_file(str(src), KEY)
    with pytest.raises(DecryptionError):
        decrypt_file(str(enc), os.urandom(32))
