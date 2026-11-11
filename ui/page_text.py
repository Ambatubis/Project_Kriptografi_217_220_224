import customtkinter as ctk
from crypto.errors import CryptoError
from crypto.super_text import decrypt_text, encrypt_text
from ui import theme as T
from ui.widgets import (Page, card, label, primary_button, secondary_button, entry, textbox,
                        status_label, set_status, get_text, set_text)


class TextPage(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.header("Super Enkripsi Teks", "Plaintext → Vigenere Cipher → AES-256-GCM → Ciphertext (Base64)")
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16)
        c = card(body)
        c.pack(fill="x", padx=12, pady=6)
        pad = {"padx": 20}
        label(c, "Pesan (plaintext)", 13, "bold").pack(anchor="w", pady=(16, 4), **pad)
        self.plain = textbox(c, 110)
        self.plain.pack(fill="x", **pad)
        label(c, "Kunci Vigenere (huruf A-Z)", 13, "bold").pack(anchor="w", pady=(12, 4), **pad)
        self.vkey = entry(c, "contoh: KUNCI")
        self.vkey.pack(fill="x", **pad)
        row = ctk.CTkFrame(c, fg_color="transparent")
        row.pack(fill="x", pady=12, **pad)
        primary_button(row, "🔒 Enkripsi", self.encrypt).pack(side="left")
        secondary_button(row, "🔓 Dekripsi", self.decrypt).pack(side="left", padx=8)
        label(c, "Ciphertext (Base64)", 13, "bold").pack(anchor="w", pady=(4, 4), **pad)
        self.cipher = textbox(c, 110)
        self.cipher.pack(fill="x", **pad)
        row2 = ctk.CTkFrame(c, fg_color="transparent")
        row2.pack(fill="x", pady=12, **pad)
        secondary_button(row2, "Salin Ciphertext", self.copy).pack(side="left")
        secondary_button(row2, "Simpan ke Brankas", self.save, width=170).pack(side="left", padx=8)
        self.status = status_label(c)
        self.status.pack(fill="x", pady=(0, 14), **pad)
        n = card(body)
        n.pack(fill="x", padx=12, pady=6)
        label(n, "ℹ Catatan: Vigenere hanya untuk aspek pembelajaran kriptografi klasik dan BUKAN perlindungan "
                 "utama. Keamanan sesungguhnya berasal dari AES-256-GCM (nonce acak + authentication tag).",
              12, color=T.MUTED, wraplength=760, justify="left").pack(padx=20, pady=14)

    def encrypt(self):
        try:
            out = encrypt_text(get_text(self.plain), self.vkey.get(), self.svc.session.get_subkey("text"))
        except CryptoError as e:
            set_status(self.status, f"✘ {e}", False)
            return
        set_text(self.cipher, out)
        self.svc.log("TEXT_ENCRYPT", "OK", f"len={len(out)}")
        set_status(self.status, "✔ Enkripsi berhasil. Nonce acak digunakan dan tag autentikasi ditambahkan.", True)

    def decrypt(self):
        try:
            out = decrypt_text(get_text(self.cipher), self.vkey.get(), self.svc.session.get_subkey("text"))
        except CryptoError as e:
            self.svc.log("TEXT_DECRYPT", "FAIL")
            set_status(self.status, f"✘ {e}", False)
            return
        set_text(self.plain, out)
        self.svc.log("TEXT_DECRYPT", "OK")
        set_status(self.status, "✔ Autentikasi AES-GCM valid. Data tidak diubah, dekripsi berhasil.", True)

    def copy(self):
        self.clipboard_clear()
        self.clipboard_append(get_text(self.cipher))
        self.app.notify("Ciphertext disalin", "success")

    def save(self):
        ct = get_text(self.cipher).strip()
        if not ct:
            set_status(self.status, "✘ Belum ada ciphertext untuk disimpan.", False)
            return
        title = ctk.CTkInputDialog(text="Judul catatan:", title="Simpan ke Brankas").get_input()
        if title:
            self.svc.save_message(title, ct)
            self.app.notify("Disimpan ke brankas (terenkripsi AES-256-GCM)", "success")
