"""Kerangka utama setelah login: sidebar + area konten."""
import customtkinter as ctk
from ui import theme as T
from ui.widgets import label


NAV = [
    ("dashboard", "🏠  Dashboard"),
    ("text", "✉  Enkripsi Teks"),
    ("files", "📁  Enkripsi File"),
    ("database", "🗄  Secure Database"),
    ("stego", "🖼  Steganografi"),
    ("chain", "⛓  Blockchain"),
    ("logs", "📋  Activity Logs"),
    ("settings", "⚙  Settings"),
]


class Shell(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=T.BG)
        self.app, self.svc = app, app.svc
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        side = ctk.CTkFrame(self, fg_color=T.CARD, corner_radius=0, width=230, border_width=1, border_color=T.BORDER)
        side.grid(row=0, column=0, sticky="nsw")
        side.grid_propagate(False)
        label(side, "🔐 SecureVault", 20, "bold", T.PRIMARY).pack(padx=20, pady=(24, 2), anchor="w")
        label(side, f"Pengguna: {self.svc.session.username}", 12, color=T.MUTED).pack(padx=20, pady=(0, 18), anchor="w")

        self.buttons = {}
        for key, text in NAV:
            b = ctk.CTkButton(side, text=text, anchor="w", height=40, corner_radius=10, font=T.font(13),
                              fg_color="transparent", text_color=T.TEXT, hover_color=T.SOFT,
                              command=lambda k=key: self.show_section(k))
            b.pack(fill="x", padx=12, pady=2)
            self.buttons[key] = b
        ctk.CTkButton(side, text="⎋  Logout", anchor="w", height=40, corner_radius=10, font=T.font(13, "bold"),
                      fg_color="#FDECEC", text_color=T.DANGER, hover_color="#F9D2D2",
                      command=self.logout).pack(side="bottom", fill="x", padx=12, pady=16)

        self.content = ctk.CTkFrame(self, fg_color=T.BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.show_section("dashboard")

    def show_section(self, key):
        from ui.page_dashboard import DashboardPage
        from ui.page_text import TextPage
        from ui.page_files import FilePage
        from ui.page_database import DatabasePage
        from ui.page_stego import StegoPage
        from ui.page_blockchain import BlockchainPage
        from ui.page_logs_settings import LogsPage, SettingsPage
        pages = {"dashboard": DashboardPage, "text": TextPage, "files": FilePage, "database": DatabasePage,
                 "stego": StegoPage, "chain": BlockchainPage, "logs": LogsPage, "settings": SettingsPage}
        for child in self.content.winfo_children():
            child.destroy()
        for k, b in self.buttons.items():
            b.configure(fg_color=T.SOFT if k == key else "transparent",
                        text_color=T.PRIMARY if k == key else T.TEXT)
        pages[key](self.content, self.app).pack(fill="both", expand=True)

    def logout(self):
        self.svc.log("LOGOUT", "OK")
        self.svc.auth.logout()
        self.app.donggle_pub = None
        self.app.notify("Anda telah logout.", "info")
        self.app.show("donggle")
