import customtkinter as ctk
from core.auth_service import AuthError
from ui import theme as T
from ui.widgets import (Page, card, label, primary_button, secondary_button, entry, status_label,
                        set_status, make_table)


class LogsPage(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.header("Activity Logs", "Riwayat aktivitas aplikasi (200 terakhir).")
        secondary_button(self, "⟳ Muat Ulang", self.reload, width=130).pack(anchor="w", padx=28, pady=4)
        frame, self.tree = make_table(self, [("t", "Waktu", 150), ("u", "User", 110), ("a", "Aksi", 150),
                                             ("s", "Status", 70), ("d", "Detail", 340)])
        frame.pack(fill="both", expand=True, padx=28, pady=(4, 24))
        self.tree.tag_configure("fail", foreground=T.DANGER)
        self.reload()

    def reload(self):
        self.tree.delete(*self.tree.get_children())
        for r in self.svc.activity.recent():
            self.tree.insert("", "end", values=(r["created_at"], r["username"] or "-", r["action"], r["status"],
                                                r["detail"] or ""), tags=("fail",) if r["status"] == "FAIL" else ())


class SettingsPage(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.header("Settings", "Pengaturan akun dan informasi keamanan.")
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16)
        c = card(body)
        c.pack(fill="x", padx=12, pady=6)
        label(c, "Ganti Password", 15, "bold").pack(anchor="w", padx=20, pady=(16, 6))
        self.old = entry(c, "Password lama", show="•")
        self.new = entry(c, "Password baru (min. 8 karakter)", show="•")
        self.new2 = entry(c, "Ulangi password baru", show="•")
        for w in (self.old, self.new, self.new2):
            w.pack(fill="x", padx=20, pady=3)
        primary_button(c, "Simpan Password", self.change, width=190).pack(anchor="w", padx=20, pady=10)
        self.status = status_label(c)
        self.status.pack(fill="x", padx=20, pady=(0, 14))

        n = card(body)
        n.pack(fill="x", padx=12, pady=6)
        label(n, "Catatan Keamanan & Keterbatasan", 15, "bold").pack(anchor="w", padx=20, pady=(16, 6))
        notes = [
            "• Password diverifikasi dengan Argon2id; kunci enkripsi diturunkan dari password (KEK) dan membuka VMK acak.",
            "• VMK hanya ada di memori selama sesi dan dihapus saat logout.",
            "• Vigenere hanya untuk pembelajaran kriptografi klasik, bukan perlindungan utama.",
            "• Blockchain adalah hash chain lokal; tidak ada konsensus/node lain.",
            "• Lupa password berarti data tidak dapat dipulihkan (konsekuensi desain).",
            "• Fernet memproses seluruh file di memori (cocok untuk file kecil-menengah).",
        ]
        for t in notes:
            label(n, t, 12, color=T.MUTED, wraplength=760, justify="left").pack(anchor="w", padx=20, pady=1)
        label(n, "", 6).pack(pady=4)

    def change(self):
        try:
            self.svc.auth.change_password(self.old.get(), self.new.get(), self.new2.get())
        except AuthError as e:
            set_status(self.status, f"✘ {e}", False)
            return
        self.svc.log("PASSWORD_CHANGE", "OK")
        for w in (self.old, self.new, self.new2):
            w.delete(0, "end")
        set_status(self.status, "✔ Password diganti. Data tetap dapat dibuka (VMK dibungkus ulang).", True)
