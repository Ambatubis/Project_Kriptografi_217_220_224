"""Sesi pengguna. VMK & sub-kunci hanya ada di RAM selama login."""
from crypto.kdf import derive_subkey

SUBKEY_LABELS = ("text", "db", "file", "stego")


class Session:
    def __init__(self):
        self.clear()

    def start(self, user_id: int, username: str, vmk: bytes):
        self.user_id, self.username = user_id, username
        self._keys = {label: derive_subkey(vmk, label) for label in SUBKEY_LABELS}
        self.active = True

    def get_subkey(self, label: str) -> bytes:
        if not self.active:
            raise PermissionError("Sesi tidak aktif.")
        return self._keys[label]

    def clear(self):
        self.user_id = None
        self.username = None
        self._keys = {}
        self.active = False
