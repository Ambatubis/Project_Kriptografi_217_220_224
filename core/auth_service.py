"""Registrasi, login, ganti password, dan manajemen kunci (VMK)."""
import os
import time
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from core import config, donggle
from crypto import kdf
from crypto.errors import DecryptionError

_ph = PasswordHasher()
_VMK_AAD = b"securevault:vmk:v1"
GENERIC_ERR = "Username atau password salah."


class AuthError(Exception):
    pass


def _wrap_vmk(kek: bytes, vmk: bytes) -> bytes:
    nonce = os.urandom(12)
    return nonce + AESGCM(kek).encrypt(nonce, vmk, _VMK_AAD)


def _unwrap_vmk(kek: bytes, blob: bytes) -> bytes:
    try:
        return AESGCM(kek).decrypt(blob[:12], blob[12:], _VMK_AAD)
    except Exception:
        raise DecryptionError("Gagal membuka kunci brankas.") from None


class AuthService:
    def __init__(self, user_repo, session):
        self.users, self.session = user_repo, session
        self._fails: dict[str, tuple[int, float]] = {}

    # ---------- registrasi ----------
    def register(self, username: str, password: str, confirm: str, drive: str) -> int:
        username = username.strip()
        if not (3 <= len(username) <= 32) or not username.replace("_", "").isalnum():
            raise AuthError("Username 3-32 karakter (huruf/angka/underscore).")
        if len(password) < 8:
            raise AuthError("Password minimal 8 karakter.")
        if password != confirm:
            raise AuthError("Konfirmasi password tidak sama.")
        if self.users.by_username(username):
            raise AuthError("Username sudah dipakai.")
        if not drive:
            raise AuthError("Pilih flashdisk untuk donggle.")
        pub = donggle.create_donggle(drive)            # tulis kunci privat ke USB
        vmk, salt = os.urandom(32), kdf.new_salt()
        wrapped = _wrap_vmk(kdf.derive_kek(password, salt), vmk)
        return self.users.create(username, _ph.hash(password), salt, wrapped, pub)

    # ---------- login ----------
    def _check_lock(self, username: str):
        n, until = self._fails.get(username, (0, 0.0))
        if n >= config.MAX_LOGIN_ATTEMPTS and time.time() < until:
            raise AuthError(f"Terlalu banyak percobaan. Coba lagi dalam {int(until - time.time())} detik.")

    def _fail(self, username: str):
        n, _ = self._fails.get(username, (0, 0.0))
        self._fails[username] = (n + 1, time.time() + config.LOCKOUT_SECONDS)

    def login(self, username: str, password: str, donggle_pub: bytes) -> str:
        """Verifikasi password + kecocokan donggle. Mulai sesi. Return username."""
        username = username.strip()
        self._check_lock(username)
        user = self.users.by_username(username)
        if user is None:
            _ph.hash(password)                         # samakan waktu respons
            self._fail(username)
            raise AuthError(GENERIC_ERR)
        try:
            _ph.verify(user["password_hash"], password)
        except (VerifyMismatchError, InvalidHashError):
            self._fail(username)
            raise AuthError(GENERIC_ERR) from None
        if bytes(user["donggle_pubkey"]) != donggle_pub:
            self._fail(username)
            raise AuthError(GENERIC_ERR)               # donggle milik akun lain
        vmk = _unwrap_vmk(kdf.derive_kek(password, bytes(user["kdf_salt"])), bytes(user["wrapped_vmk"]))
        self._fails.pop(username, None)
        self.session.start(user["id"], user["username"], vmk)
        return user["username"]

    def logout(self):
        self.session.clear()

    # ---------- ganti password (VMK dibungkus ulang, data tidak perlu dienkripsi ulang) ----------
    def change_password(self, old: str, new: str, confirm: str):
        if len(new) < 8:
            raise AuthError("Password baru minimal 8 karakter.")
        if new != confirm:
            raise AuthError("Konfirmasi password tidak sama.")
        user = self.users.by_username(self.session.username)
        try:
            _ph.verify(user["password_hash"], old)
        except (VerifyMismatchError, InvalidHashError):
            raise AuthError("Password lama salah.") from None
        vmk = _unwrap_vmk(kdf.derive_kek(old, bytes(user["kdf_salt"])), bytes(user["wrapped_vmk"]))
        salt = kdf.new_salt()
        self.users.update_credentials(user["id"], _ph.hash(new), salt, _wrap_vmk(kdf.derive_kek(new, salt), vmk))
