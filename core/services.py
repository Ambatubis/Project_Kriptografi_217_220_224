"""Container layanan: merangkai DB, sesi, auth, log, dan blockchain."""
import hashlib
import json
from blockchain.chain import Blockchain
from core import config
from core.auth_service import AuthService
from core.session import Session
from crypto import aes_gcm
from database import repository as R
from database.db import Database

SENSITIVE_ACTIONS = {"REGISTER", "LOGIN", "LOGIN_FAILED", "LOGOUT", "FILE_ENCRYPT", "FILE_DECRYPT",
                     "TEXT_ENCRYPT", "STEGO_EMBED", "STEGO_EXTRACT", "MESSAGE_SAVE", "MESSAGE_DELETE", "PASSWORD_CHANGE"}


class Services:
    def __init__(self, db_path=config.DB_PATH):
        self.db = Database(db_path)
        self.session = Session()
        self.users = R.UserRepository(self.db)
        self.messages = R.MessageRepository(self.db)
        self.files = R.FileRepository(self.db)
        self.stego = R.StegoRepository(self.db)
        self.activity = R.ActivityRepository(self.db)
        self.chain = Blockchain(R.BlockchainRepository(self.db))
        self.auth = AuthService(self.users, self.session)

    def log(self, action: str, status: str = "OK", detail: str = "", user_id=None):
        """Catat ke activity_logs dan (untuk aktivitas penting) ke blockchain.
        JANGAN pernah memasukkan isi pesan/password ke `detail`."""
        uid = user_id if user_id is not None else self.session.user_id
        self.activity.add(uid, action, status, detail)
        if action in SENSITIVE_ACTIONS:
            self.chain.add_block(json.dumps({"user_id": uid, "action": action, "status": status,
                                             "detail_sha256": hashlib.sha256(detail.encode()).hexdigest()[:16]},
                                            sort_keys=True))

    # ---------- brankas pesan (AES-256-GCM dengan key_db) ----------
    def save_message(self, title: str, content: str) -> int:
        k = self.session.get_subkey("db")
        mid = self.messages.add(self.session.user_id,
                                aes_gcm.encrypt(k, title.encode(), b"title"),
                                aes_gcm.encrypt(k, content.encode(), b"message"))
        self.log("MESSAGE_SAVE", "OK", f"id={mid}")
        return mid

    def read_message(self, msg_id: int) -> tuple[str, str]:
        row = self.messages.get(self.session.user_id, msg_id)
        k = self.session.get_subkey("db")
        return (aes_gcm.decrypt(k, bytes(row["title_ct"]), b"title").decode(),
                aes_gcm.decrypt(k, bytes(row["ciphertext"]), b"message").decode())

    def list_message_titles(self) -> list[tuple[int, str, str]]:
        k = self.session.get_subkey("db")
        out = []
        for r in self.messages.list(self.session.user_id):
            try:
                out.append((r["id"], aes_gcm.decrypt(k, bytes(r["title_ct"]), b"title").decode(), r["created_at"]))
            except Exception:
                out.append((r["id"], "[tidak dapat didekripsi]", r["created_at"]))
        return out
