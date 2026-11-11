from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog
from core import config
from crypto.errors import CryptoError
from crypto.fernet_file import decrypt_file, encrypt_file
from ui import theme as T
from ui.widgets import (Page, card, label, primary_button, secondary_button, status_label, set_status,
                        make_table)


class FilePage(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.header("Enkripsi File (Fernet)", f"Hasil disimpan sebagai *{config.VAULT_EXT}. File asli TIDAK dihapus.")
        c = card(self)
        c.pack(fill="x", padx=28, pady=6)
        row = ctk.CTkFrame(c, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=18)
        primary_button(row, "🔒 Pilih & Enkripsi File", self.encrypt, width=220).pack(side="left")
        secondary_button(row, "🔓 Pilih & Dekripsi .svault", self.decrypt, width=230).pack(side="left", padx=10)
        self.status = status_label(c)
        self.status.pack(fill="x", padx=20, pady=(0, 16))
        label(self, "Riwayat File Terenkripsi", 15, "bold").pack(anchor="w", padx=30, pady=(8, 4))
        frame, self.tree = make_table(self, [("name", "Nama Asli", 220), ("path", "Lokasi .svault", 360),
                                             ("size", "Ukuran", 90), ("sha", "SHA-256 (enkripsi)", 200),
                                             ("time", "Waktu", 140)])
        frame.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        self.reload()

    def reload(self):
        self.tree.delete(*self.tree.get_children())
        for r in self.svc.files.list(self.svc.session.user_id):
            self.tree.insert("", "end", values=(r["original_name"], r["vault_path"], f"{r['file_size']:,} B",
                                                r["sha256_encrypted"][:20] + "…", r["created_at"]))

    def encrypt(self):
        src = filedialog.askopenfilename(title="Pilih file yang akan dienkripsi")
        if not src:
            return
        try:
            out, sha = encrypt_file(src, self.svc.session.get_subkey("file"))
        except (CryptoError, OSError) as e:
            self.svc.log("FILE_ENCRYPT", "FAIL")
            set_status(self.status, f"✘ Gagal: {e}", False)
            self.app.notify("Enkripsi file gagal", "error")
            return
        self.svc.files.add(self.svc.session.user_id, Path(src).name, str(out), out.stat().st_size, sha)
        self.svc.log("FILE_ENCRYPT", "OK", f"{Path(src).name} sha={sha[:16]}")
        set_status(self.status, f"✔ Berhasil: {out}", True)
        self.app.notify("File terenkripsi", "success")
        self.reload()

    def decrypt(self):
        src = filedialog.askopenfilename(title="Pilih file .svault", filetypes=[("SecureVault", f"*{config.VAULT_EXT}")])
        if not src:
            return
        try:
            out = decrypt_file(src, self.svc.session.get_subkey("file"))
        except (CryptoError, OSError) as e:
            self.svc.log("FILE_DECRYPT", "FAIL")
            set_status(self.status, f"✘ {e}", False)
            self.app.notify("Dekripsi file gagal", "error")
            return
        self.svc.log("FILE_DECRYPT", "OK", Path(out).name)
        set_status(self.status, f"✔ File dipulihkan: {out}", True)
        self.app.notify("File berhasil didekripsi", "success")
