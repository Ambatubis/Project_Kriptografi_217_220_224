class CryptoError(Exception):
    """Kesalahan kriptografi umum (pesan aman, tanpa detail sensitif)."""

class DecryptionError(CryptoError):
    """Dekripsi gagal: kunci salah atau data rusak/dimodifikasi."""
