"""Steganografi LSB pada gambar PNG (3 bit per piksel: R,G,B).

Payload = MAGIC(4) || panjang(4, big-endian) || data.
Data yang disisipkan adalah CIPHERTEXT AES-256-GCM (dienkripsi lebih dulu).
"""
import struct
from pathlib import Path
from PIL import Image
from crypto import aes_gcm
from crypto.errors import CryptoError, DecryptionError

MAGIC = b"SVLT"
HEADER = len(MAGIC) + 4
AAD = b"securevault:stego:v1"


def _open_png(path: str) -> Image.Image:
    p = Path(path)
    if p.suffix.lower() != ".png":
        raise CryptoError("Hanya format PNG yang didukung (lossless).")
    try:
        return Image.open(p).convert("RGB")
    except Exception:
        raise CryptoError("Gambar tidak dapat dibuka.") from None


def capacity_bytes(path: str) -> int:
    w, h = _open_png(path).size
    return max(0, (w * h * 3) // 8 - HEADER)


def embed(cover: str, message: str, key: bytes, out_path: str) -> int:
    """Enkripsi pesan, sisipkan ke gambar. Return ukuran payload (byte)."""
    img = _open_png(cover)
    cipher = aes_gcm.encrypt(key, message.encode("utf-8"), AAD)
    payload = MAGIC + struct.pack(">I", len(cipher)) + cipher
    if len(payload) * 8 > img.width * img.height * 3:
        raise CryptoError(f"Pesan terlalu besar. Kapasitas maksimum ± {capacity_bytes(cover)} byte setelah enkripsi.")
    px = bytearray(img.tobytes())
    bit_i = 0
    for byte in payload:
        for s in range(7, -1, -1):
            px[bit_i] = (px[bit_i] & 0xFE) | ((byte >> s) & 1)
            bit_i += 1
    Image.frombytes("RGB", img.size, bytes(px)).save(out_path, format="PNG")
    return len(payload)


def _read_bytes(px: bytes, start_byte: int, count: int) -> bytes:
    out = bytearray()
    for b in range(start_byte, start_byte + count):
        v = 0
        for k in range(8):
            v = (v << 1) | (px[b * 8 + k] & 1)
        out.append(v)
    return bytes(out)


def extract(stego_path: str, key: bytes) -> str:
    img = _open_png(stego_path)
    px = img.tobytes()
    total = len(px) // 8
    if total < HEADER:
        raise CryptoError("Tidak ada pesan tersembunyi.")
    head = _read_bytes(px, 0, HEADER)
    if head[:4] != MAGIC:
        raise CryptoError("Tidak ditemukan pesan SecureVault pada gambar ini.")
    length = struct.unpack(">I", head[4:])[0]
    if length < 28 or HEADER + length > total:
        raise CryptoError("Data tersembunyi rusak.")
    cipher = _read_bytes(px, HEADER, length)
    try:
        return aes_gcm.decrypt(key, cipher, AAD).decode("utf-8")
    except DecryptionError:
        raise DecryptionError("Gagal mendekripsi: kunci salah atau gambar telah dimodifikasi.") from None
