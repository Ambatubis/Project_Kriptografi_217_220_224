"""Vigenere Cipher (klasik). Hanya huruf A-Z yang digeser; karakter lain tetap.

CATATAN AKADEMIS: Vigenere dipakai untuk aspek pembelajaran kriptografi klasik.
Perlindungan keamanan utama berasal dari AES-256-GCM.
"""
from .errors import CryptoError


def _clean_key(key: str) -> list[int]:
    shifts = [ord(c) - 65 for c in key.upper() if "A" <= c <= "Z"]
    if not shifts:
        raise CryptoError("Kunci Vigenere harus berisi minimal satu huruf (A-Z).")
    return shifts


def _process(text: str, key: str, sign: int) -> str:
    shifts, out, i = _clean_key(key), [], 0
    for ch in text:
        if "A" <= ch <= "Z":
            base = 65
        elif "a" <= ch <= "z":
            base = 97
        else:
            out.append(ch)
            continue
        out.append(chr((ord(ch) - base + sign * shifts[i % len(shifts)]) % 26 + base))
        i += 1
    return "".join(out)


def encrypt(plaintext: str, key: str) -> str:
    return _process(plaintext, key, +1)


def decrypt(ciphertext: str, key: str) -> str:
    return _process(ciphertext, key, -1)
