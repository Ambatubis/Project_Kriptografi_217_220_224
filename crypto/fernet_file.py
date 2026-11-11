"""Enkripsi file dengan Fernet. File asli TIDAK dihapus."""
import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from core.config import VAULT_EXT, MAX_FILE_SIZE_MB
from .errors import CryptoError, DecryptionError


def _fernet(key32: bytes) -> Fernet:
    return Fernet(base64.urlsafe_b64encode(key32))


def encrypt_file(src: str, key32: bytes, out_dir: str | None = None) -> tuple[Path, str]:
    """Return (path .svault, sha256 hex dari file terenkripsi)."""
    src_p = Path(src)
    if not src_p.is_file():
        raise CryptoError("File tidak ditemukan.")
    if src_p.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise CryptoError(f"File terlalu besar (maksimum {MAX_FILE_SIZE_MB} MB).")
    token = _fernet(key32).encrypt(src_p.read_bytes())
    dest = Path(out_dir or src_p.parent) / (src_p.name + VAULT_EXT)
    dest.write_bytes(token)
    return dest, hashlib.sha256(token).hexdigest()


def decrypt_file(vault_file: str, key32: bytes, out_dir: str | None = None) -> Path:
    v = Path(vault_file)
    if not v.is_file() or v.suffix != VAULT_EXT:
        raise CryptoError("Pilih file berekstensi .svault.")
    try:
        data = _fernet(key32).decrypt(v.read_bytes())
    except InvalidToken:
        raise DecryptionError("Dekripsi gagal: kunci salah atau file rusak.") from None
    dest = Path(out_dir or v.parent) / v.name[: -len(VAULT_EXT)]
    n = 1
    while dest.exists():                      # jangan menimpa file yang sudah ada
        dest = dest.with_name(f"{dest.stem}_pulih{n}{dest.suffix}")
        n += 1
    dest.write_bytes(data)
    return dest
