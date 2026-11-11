"""Repository: seluruh query SQL ada di sini."""
from blockchain.block import Block


class UserRepository:
    def __init__(self, db): self.db = db

    def create(self, username, password_hash, kdf_salt, wrapped_vmk, pubkey) -> int:
        return self.db.execute(
            "INSERT INTO users(username,password_hash,kdf_salt,wrapped_vmk,donggle_pubkey) VALUES(?,?,?,?,?)",
            (username, password_hash, kdf_salt, wrapped_vmk, pubkey)).lastrowid

    def by_username(self, username):
        rows = self.db.query("SELECT * FROM users WHERE username=?", (username,))
        return rows[0] if rows else None

    def by_pubkey(self, pubkey):
        rows = self.db.query("SELECT * FROM users WHERE donggle_pubkey=?", (pubkey,))
        return rows[0] if rows else None

    def count(self) -> int:
        return self.db.query("SELECT COUNT(*) c FROM users")[0]["c"]

    def update_credentials(self, user_id, password_hash, kdf_salt, wrapped_vmk):
        self.db.execute("UPDATE users SET password_hash=?,kdf_salt=?,wrapped_vmk=? WHERE id=?",
                        (password_hash, kdf_salt, wrapped_vmk, user_id))


class MessageRepository:
    def __init__(self, db): self.db = db

    def add(self, user_id, title_ct, ciphertext) -> int:
        return self.db.execute("INSERT INTO secure_messages(user_id,title_ct,ciphertext) VALUES(?,?,?)",
                               (user_id, title_ct, ciphertext)).lastrowid

    def list(self, user_id):
        return self.db.query("SELECT * FROM secure_messages WHERE user_id=? ORDER BY id DESC", (user_id,))

    def get(self, user_id, msg_id):
        r = self.db.query("SELECT * FROM secure_messages WHERE user_id=? AND id=?", (user_id, msg_id))
        return r[0] if r else None

    def delete(self, user_id, msg_id):
        self.db.execute("DELETE FROM secure_messages WHERE user_id=? AND id=?", (user_id, msg_id))

    def count(self, user_id):
        return self.db.query("SELECT COUNT(*) c FROM secure_messages WHERE user_id=?", (user_id,))[0]["c"]


class FileRepository:
    def __init__(self, db): self.db = db

    def add(self, user_id, name, path, size, sha):
        self.db.execute("INSERT INTO encrypted_files(user_id,original_name,vault_path,file_size,sha256_encrypted) VALUES(?,?,?,?,?)",
                        (user_id, name, path, size, sha))

    def list(self, user_id):
        return self.db.query("SELECT * FROM encrypted_files WHERE user_id=? ORDER BY id DESC", (user_id,))

    def count(self, user_id):
        return self.db.query("SELECT COUNT(*) c FROM encrypted_files WHERE user_id=?", (user_id,))[0]["c"]


class StegoRepository:
    def __init__(self, db): self.db = db

    def add(self, user_id, cover, out, size):
        self.db.execute("INSERT INTO steganography_records(user_id,cover_image_name,output_path,payload_size) VALUES(?,?,?,?)",
                        (user_id, cover, out, size))

    def list(self, user_id):
        return self.db.query("SELECT * FROM steganography_records WHERE user_id=? ORDER BY id DESC", (user_id,))

    def count(self, user_id):
        return self.db.query("SELECT COUNT(*) c FROM steganography_records WHERE user_id=?", (user_id,))[0]["c"]


class ActivityRepository:
    def __init__(self, db): self.db = db

    def add(self, user_id, action, status, detail=""):
        self.db.execute("INSERT INTO activity_logs(user_id,action,status,detail) VALUES(?,?,?,?)",
                        (user_id, action, status, detail))

    def recent(self, limit=200):
        return self.db.query("SELECT a.*, u.username FROM activity_logs a LEFT JOIN users u ON u.id=a.user_id "
                             "ORDER BY a.id DESC LIMIT ?", (limit,))


class BlockchainRepository:
    def __init__(self, db): self.db = db

    @staticmethod
    def _to_block(r) -> Block:
        return Block(r["block_index"], r["timestamp"], r["data"], r["previous_hash"], r["current_hash"])

    def count(self) -> int:
        return self.db.query("SELECT COUNT(*) c FROM blockchain_records")[0]["c"]

    def insert(self, b: Block):
        self.db.execute("INSERT INTO blockchain_records(block_index,timestamp,data,previous_hash,current_hash) VALUES(?,?,?,?,?)",
                        (b.index, b.timestamp, b.data, b.previous_hash, b.current_hash))

    def last(self) -> Block:
        return self._to_block(self.db.query("SELECT * FROM blockchain_records ORDER BY block_index DESC LIMIT 1")[0])

    def all(self) -> list[Block]:
        return [self._to_block(r) for r in self.db.query("SELECT * FROM blockchain_records ORDER BY block_index")]
