"""USB Donggle: deteksi flashdisk + challenge-response Ed25519.

Kunci privat disimpan di donggle_key.dat (flashdisk). Kunci publik disimpan di DB.
Verifikasi: aplikasi membuat challenge acak -> donggle menandatangani -> diverifikasi
dengan kunci publik di DB. Menyalin NAMA file saja tidak cukup.
"""
import base64
import json
import os
import string
from pathlib import Path
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from core import config

DRIVE_REMOVABLE = 2


class DonggleError(Exception):
    pass


def list_removable_drives() -> list[str]:
    drives = list(config.DEV_DONGGLE_DIRS)
    if config.IS_WINDOWS:
        import ctypes
        mask = ctypes.windll.kernel32.GetLogicalDrives()
        for i, letter in enumerate(string.ascii_uppercase):
            if mask & (1 << i):
                root = f"{letter}:\\"
                if ctypes.windll.kernel32.GetDriveTypeW(root) == DRIVE_REMOVABLE:
                    drives.append(root)
    return drives


def _raw_pub(priv: Ed25519PrivateKey) -> bytes:
    return priv.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def create_donggle(drive: str) -> bytes:
    """Buat pasangan kunci, tulis donggle_key.dat ke drive. Return public key (32 byte)."""
    path = Path(drive) / config.DONGGLE_FILENAME
    if path.exists():
        raise DonggleError("Flashdisk ini sudah berisi donggle_key.dat. Gunakan flashdisk lain.")
    priv = Ed25519PrivateKey.generate()
    raw_priv = priv.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                                  serialization.NoEncryption())
    try:
        path.write_text(json.dumps({"v": 1, "private_key": base64.b64encode(raw_priv).decode()}))
    except OSError:
        raise DonggleError("Tidak dapat menulis ke flashdisk.") from None
    return _raw_pub(priv)


def _load_private(drive: str) -> Ed25519PrivateKey:
    path = Path(drive) / config.DONGGLE_FILENAME
    try:
        data = json.loads(path.read_text())
        return Ed25519PrivateKey.from_private_bytes(base64.b64decode(data["private_key"]))
    except Exception:
        raise DonggleError("Donggle tidak ditemukan atau tidak valid.") from None


def verify_donggle(drive: str, user_repo) -> bytes:
    """Challenge-response. Return public key donggle jika valid; selain itu DonggleError."""
    priv = _load_private(drive)
    pub = _raw_pub(priv)
    user = user_repo.by_pubkey(pub)
    if user is None:
        raise DonggleError("Donggle tidak ditemukan atau tidak valid.")   # pesan sengaja generik
    challenge = os.urandom(32)
    signature = priv.sign(challenge)                                        # "donggle" menandatangani
    try:
        Ed25519PublicKey.from_public_bytes(bytes(user["donggle_pubkey"])).verify(signature, challenge)
    except InvalidSignature:
        raise DonggleError("Donggle tidak ditemukan atau tidak valid.") from None
    return pub


def find_and_verify(user_repo) -> bytes:
    """Cek semua flashdisk yang terdeteksi."""
    for d in list_removable_drives():
        if (Path(d) / config.DONGGLE_FILENAME).exists():
            try:
                return verify_donggle(d, user_repo)
            except DonggleError:
                continue
    raise DonggleError("Donggle tidak ditemukan atau tidak valid.")
