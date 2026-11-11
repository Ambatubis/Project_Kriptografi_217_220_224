import customtkinter as ctk
from ui import theme as T
from ui.widgets import Page, card, label


class DashboardPage(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        uid = self.svc.session.user_id
        self.header(f"Halo, {self.svc.session.username} 👋", "Ringkasan brankas digital Anda.")
        ok, _, msg = self.svc.chain.verify()
        stats = [
            ("✉ Pesan Tersimpan", self.svc.messages.count(uid), T.PRIMARY),
            ("📁 File Terenkripsi", self.svc.files.count(uid), T.PRIMARY),
            ("🖼 Gambar Stego", self.svc.stego.count(uid), T.PRIMARY),
            ("⛓ Jumlah Blok", len(self.svc.chain.blocks()), T.PRIMARY),
        ]
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=22, pady=8)
        for i, (name, val, color) in enumerate(stats):
            grid.grid_columnconfigure(i, weight=1, uniform="c")
            c = card(grid)
            c.grid(row=0, column=i, padx=6, sticky="nsew")
            label(c, name, 13, color=T.MUTED).pack(anchor="w", padx=18, pady=(16, 0))
            label(c, str(val), 34, "bold", color).pack(anchor="w", padx=18, pady=(0, 14))

        c = card(self)
        c.pack(fill="x", padx=28, pady=10)
        label(c, "Status Integritas Blockchain", 15, "bold").pack(anchor="w", padx=20, pady=(16, 2))
        label(c, ("✔ " if ok else "✘ ") + msg, 13, color=T.SUCCESS if ok else T.DANGER,
              wraplength=800, justify="left").pack(anchor="w", padx=20, pady=(0, 16))

        c2 = card(self)
        c2.pack(fill="x", padx=28, pady=4)
        label(c2, "Lapisan Keamanan Aktif", 15, "bold").pack(anchor="w", padx=20, pady=(16, 4))
        for t in ("✔ Donggle USB (challenge-response Ed25519)", "✔ Password Argon2id",
                  "✔ Windows Hello", "✔ AES-256-GCM, Fernet, LSB, hash chain SHA-256"):
            label(c2, t, 13, color=T.MUTED).pack(anchor="w", padx=20)
        label(c2, "", 6).pack(pady=4)
