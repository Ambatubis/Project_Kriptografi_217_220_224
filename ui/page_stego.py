from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk
from core import config
from crypto.errors import CryptoError
from steganography import lsb
from ui import theme as T
from ui.widgets import (Page, card, label, primary_button, secondary_button, textbox, status_label,
                        set_status, get_text, set_text)


class StegoPage(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.header("Steganografi Gambar (LSB)", "Pesan dienkripsi AES-256-GCM, lalu disisipkan ke LSB piksel PNG.")
        tabs = ctk.CTkTabview(self, fg_color=T.CARD, segmented_button_selected_color=T.PRIMARY,
                              segmented_button_selected_hover_color=T.PRIMARY_HOVER)
        tabs.pack(fill="both", expand=True, padx=28, pady=(4, 24))
        emb, ext = tabs.add("Sisipkan Pesan"), tabs.add("Ekstrak Pesan")

        self.cover = None
        row = ctk.CTkFrame(emb, fg_color="transparent")
        row.pack(fill="x", pady=8)
        secondary_button(row, "Pilih Gambar PNG", self.pick_cover, width=170).pack(side="left")
        self.cover_lbl = label(row, "Belum ada gambar", 12, color=T.MUTED)
        self.cover_lbl.pack(side="left", padx=12)
        label(emb, "Pesan rahasia", 13, "bold").pack(anchor="w")
        self.msg = textbox(emb, 130)
        self.msg.pack(fill="x", pady=6)
        primary_button(emb, "Sisipkan & Simpan PNG", self.embed, width=220).pack(anchor="w", pady=6)
        self.status1 = status_label(emb)
        self.status1.pack(fill="x")

        self.stego = None
        row = ctk.CTkFrame(ext, fg_color="transparent")
        row.pack(fill="x", pady=8)
        secondary_button(row, "Pilih Gambar Stego", self.pick_stego, width=170).pack(side="left")
        self.stego_lbl = label(row, "Belum ada gambar", 12, color=T.MUTED)
        self.stego_lbl.pack(side="left", padx=12)
        primary_button(ext, "Ekstrak & Dekripsi", self.extract, width=200).pack(anchor="w", pady=6)
        self.out = textbox(ext, 150)
        self.out.pack(fill="x", pady=6)
        self.status2 = status_label(ext)
        self.status2.pack(fill="x")

    def pick_cover(self):
        p = filedialog.askopenfilename(title="Pilih PNG", filetypes=[("PNG", "*.png")])
        if not p:
            return
        try:
            cap = lsb.capacity_bytes(p)
        except CryptoError as e:
            return set_status(self.status1, f"✘ {e}", False)
        self.cover = p
        self.cover_lbl.configure(text=f"{Path(p).name}  (kapasitas ± {cap:,} byte)")

    def embed(self):
        if not self.cover or not get_text(self.msg).strip():
            return set_status(self.status1, "✘ Pilih gambar PNG dan isi pesan.", False)
        out = filedialog.asksaveasfilename(title="Simpan gambar stego", defaultextension=".png",
                                           initialfile="stego_" + Path(self.cover).name,
                                           initialdir=str(config.STEGO_DIR), filetypes=[("PNG", "*.png")])
        if not out:
            return
        try:
            size = lsb.embed(self.cover, get_text(self.msg), self.svc.session.get_subkey("stego"), out)
        except (CryptoError, OSError) as e:
            self.svc.log("STEGO_EMBED", "FAIL")
            return set_status(self.status1, f"✘ {e}", False)
        self.svc.stego.add(self.svc.session.user_id, Path(self.cover).name, out, size)
        self.svc.log("STEGO_EMBED", "OK", f"payload={size}")
        set_status(self.status1, f"✔ Pesan tersembunyi di: {out}", True)
        self.app.notify("Steganografi berhasil", "success")

    def pick_stego(self):
        p = filedialog.askopenfilename(title="Pilih PNG stego", filetypes=[("PNG", "*.png")])
        if p:
            self.stego = p
            self.stego_lbl.configure(text=Path(p).name)

    def extract(self):
        if not self.stego:
            return set_status(self.status2, "✘ Pilih gambar terlebih dahulu.", False)
        try:
            msg = lsb.extract(self.stego, self.svc.session.get_subkey("stego"))
        except CryptoError as e:
            self.svc.log("STEGO_EXTRACT", "FAIL")
            return set_status(self.status2, f"✘ {e}", False)
        set_text(self.out, msg)
        self.svc.log("STEGO_EXTRACT", "OK")
        set_status(self.status2, "✔ Pesan berhasil diekstrak dan didekripsi (autentikasi valid).", True)
