"""Derivasi kunci: Argon2id (password -> KEK) dan HKDF (VMK -> sub-kunci)."""
import os
from argon2.low_level import Type, hash_secret_raw
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

ARGON_TIME_COST = 3
ARGON_MEMORY_KIB = 64 * 1024   # 64 MiB
ARGON_PARALLELISM = 2


def new_salt(n: int = 16) -> bytes:
    return os.urandom(n)


def derive_kek(password: str, salt: bytes) -> bytes:
    """Password -> Key Encryption Key 32 byte memakai Argon2id (raw)."""
    return hash_secret_raw(
        secret=password.encode("utf-8"), salt=salt,
        time_cost=ARGON_TIME_COST, memory_cost=ARGON_MEMORY_KIB,
        parallelism=ARGON_PARALLELISM, hash_len=32, type=Type.ID,
    )


def derive_subkey(vmk: bytes, label: str) -> bytes:
    """VMK -> sub-kunci 32 byte per fitur (label berbeda = kunci berbeda)."""
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=b"securevault:" + label.encode()).derive(vmk)
