"""Super enkripsi teks: Plaintext -> Vigenere -> AES-256-GCM -> Base64."""
import base64
from . import aes_gcm, vigenere
from .errors import DecryptionError

AAD = b"securevault:text:v1"


def encrypt_text(plaintext: str, vigenere_key: str, aes_key: bytes) -> str:
    stage1 = vigenere.encrypt(plaintext, vigenere_key)
    blob = aes_gcm.encrypt(aes_key, stage1.encode("utf-8"), AAD)
    return base64.b64encode(blob).decode("ascii")


def decrypt_text(ciphertext_b64: str, vigenere_key: str, aes_key: bytes) -> str:
    try:
        blob = base64.b64decode(ciphertext_b64.strip(), validate=True)
    except Exception:
        raise DecryptionError("Format ciphertext tidak valid.") from None
    stage1 = aes_gcm.decrypt(aes_key, blob, AAD).decode("utf-8")  # integritas diverifikasi di sini
    return vigenere.decrypt(stage1, vigenere_key)
