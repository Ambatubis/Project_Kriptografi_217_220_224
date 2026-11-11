"""AES-256-GCM. Format: nonce(12) || ciphertext || tag(16)."""
import os
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .errors import CryptoError, DecryptionError

NONCE_SIZE = 12


def encrypt(key: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
    if len(key) != 32:
        raise CryptoError("Kunci AES harus 32 byte (AES-256).")
    nonce = os.urandom(NONCE_SIZE)          # nonce unik tiap enkripsi
    return nonce + AESGCM(key).encrypt(nonce, plaintext, aad or None)


def decrypt(key: bytes, blob: bytes, aad: bytes = b"") -> bytes:
    if len(blob) < NONCE_SIZE + 16:
        raise DecryptionError("Data tidak valid.")
    try:
        return AESGCM(key).decrypt(blob[:NONCE_SIZE], blob[NONCE_SIZE:], aad or None)
    except InvalidTag:
        raise DecryptionError("Dekripsi gagal: kunci salah atau data telah diubah.") from None
