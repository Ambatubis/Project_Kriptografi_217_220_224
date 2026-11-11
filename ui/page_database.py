import customtkinter as ctk
from crypto.errors import CryptoError
from ui import theme as T
from ui.widgets import (Page, card, label, primary_button, secondary_button, danger_button, entry, textbox,
                        status_label, set_status, make_table, get_text, set_text)


class DatabasePage(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.header("Secure Database", "Catatan rahasia disimpan sebagai ciphertext AES-256-GCM di SQLite.")
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=(4, 24))
        wrap.grid_columnconfigure((0, 1), weight=1, uniform="x")
        wrap.grid_rowconfigure(0, weight=1)

        left = card(wrap)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        label(left, "Catatan Tersimpan", 15, "bold").pack(anchor="w", padx=18, pady=(16, 6))
        frame, self.tree = make_table(left, [("id", "ID", 45), ("title", "Judul", 200), ("time", "Dibuat", 130)])
        frame.pack(fill="both", expand=True, padx=14)
        row = ctk.CTkFrame(left, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=12)
        secondary_button(row, "Buka (dekripsi)", self.open, width=140).pack(side="left")
        secondary_button(row, "Lihat Ciphertext", self.raw, width=140).pack(side="left", padx=6)
        danger_button(row, "Hapus", self.delete, width=80).pack(side="left")

        right = card(wrap)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        label(right, "Catatan Baru / Isi", 15, "bold").pack(anchor="w", padx=18, pady=(16, 6))
        self.title_entry = entry(right, "Judul")
        self.title_entry.pack(fill="x", padx=18)
        self.content = textbox(right, 200)
        self.content.pack(fill="both", expand=True, padx=18, pady=10)
        primary_button(right, "💾 Simpan (terenkripsi)", self.save, width=220).pack(anchor="w", padx=18)
        self.status = status_label(right)
        self.status.configure(wraplength=380)
        self.status.pack(fill="x", padx=18, pady=12)
        self.reload()

    def reload(self):
        self.tree.delete(*self.tree.get_children())
        for mid, title, created in self.svc.list_message_titles():
            self.tree.insert("", "end", values=(mid, title, created))

    def _selected(self):
        sel = self.tree.selection()
        return int(self.tree.item(sel[0])["values"][0]) if sel else None

    def save(self):
        t, c = self.title_entry.get().strip(), get_text(self.content)
        if not t or not c.strip():
            set_status(self.status, "✘ Judul dan isi wajib diisi.", False)
            return
        self.svc.save_message(t, c)
        self.title_entry.delete(0, "end")
        set_text(self.content, "")
        set_status(self.status, "✔ Tersimpan sebagai ciphertext AES-256-GCM.", True)
        self.reload()

    def open(self):
        mid = self._selected()
        if mid is None:
            return set_status(self.status, "Pilih catatan terlebih dahulu.", False)
        try:
            t, c = self.svc.read_message(mid)
        except CryptoError as e:
            return set_status(self.status, f"✘ {e}", False)
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, t)
        set_text(self.content, c)
        set_status(self.status, "✔ Berhasil didekripsi dan integritas terverifikasi.", True)

    def raw(self):
        mid = self._selected()
        if mid is None:
            return set_status(self.status, "Pilih catatan terlebih dahulu.", False)
        ct = bytes(self.svc.messages.get(self.svc.session.user_id, mid)["ciphertext"])
        set_status(self.status, f"Ciphertext di database (hex): {ct.hex()[:120]}…")

    def delete(self):
        mid = self._selected()
        if mid is None:
            return
        self.svc.messages.delete(self.svc.session.user_id, mid)
        self.svc.log("MESSAGE_DELETE", "OK", f"id={mid}")
        self.reload()
