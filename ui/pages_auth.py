"""Halaman 1-4: Splash, Donggle, Registrasi, Login, Biometrik."""
import threading
import customtkinter as ctk
from core import donggle, windows_hello
from core.auth_service import AuthError
from ui import theme as T
from ui.widgets import (card, label, primary_button, secondary_button, entry, status_label,
                        set_status)


class _Center(ctk.CTkFrame):
    def __init__(self, master, app, width=420):
        super().__init__(master, fg_color=T.BG)
        self.app, self.svc = app, app.svc
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.box = card(self, width=width)
        self.box.grid(row=0, column=0)
        self.inner = ctk.CTkFrame(self.box, fg_color="transparent")
        self.inner.pack(padx=36, pady=32)


class SplashPage(_Center):
    def __init__(self, master, app):
        super().__init__(master, app)
        label(self.inner, "🔐", 56).pack()
        label(self.inner, "SecureVault", 30, "bold", T.PRIMARY).pack(pady=(4, 0))
        label(self.inner, "Brankas Digital: Super Enkripsi, Steganografi & Blockchain", 12, color=T.MUTED).pack(pady=(2, 18))
        self.bar = ctk.CTkProgressBar(self.inner, width=280, progress_color=T.PRIMARY)
        self.bar.set(0)
        self.bar.pack()
        self._v = 0.0
        self._tick()

    def _tick(self):
        self._v += 0.04
        self.bar.set(min(self._v, 1))
        if self._v >= 1:
            self.app.show("donggle")
        else:
            self.after(50, self._tick)


class DonggleVerifyPage(_Center):
    def __init__(self, master, app):
        super().__init__(master, app)
        label(self.inner, "🔑 Verifikasi Donggle", 22, "bold").pack()
        label(self.inner, "Colok flashdisk donggle Anda, lalu tekan Verifikasi.", 12, color=T.MUTED).pack(pady=(4, 14))
        self.drives = label(self.inner, "", 12, color=T.MUTED)
        self.drives.pack(pady=(0, 10))
        self.status = status_label(self.inner)
        self.status.configure(wraplength=340)
        self.status.pack(pady=(0, 10))
        primary_button(self.inner, "Verifikasi Donggle", self.verify, width=260).pack(pady=4)
        secondary_button(self.inner, "Registrasi Akun Baru", lambda: app.show("register"), width=260).pack(pady=4)
        self._refresh()

    def _refresh(self):
        d = donggle.list_removable_drives()
        self.drives.configure(text=("Flashdisk terdeteksi: " + ", ".join(d)) if d else "Tidak ada flashdisk terdeteksi.")

    def verify(self):
        self._refresh()
        try:
            self.app.donggle_pub = donggle.find_and_verify(self.svc.users)
        except donggle.DonggleError as e:
            self.svc.log("DONGGLE_VERIFY", "FAIL")
            set_status(self.status, f"✘ {e}", False)
            self.app.notify("Donggle tidak valid", "error")
            return
        self.svc.log("DONGGLE_VERIFY", "OK")
        self.app.notify("Donggle valid", "success")
        self.app.show("login")


class RegisterPage(_Center):
    def __init__(self, master, app):
        super().__init__(master, app, 440)
        label(self.inner, "Registrasi Akun", 22, "bold").pack()
        label(self.inner, "Donggle (kunci privat) akan ditulis ke flashdisk Anda.", 12, color=T.MUTED).pack(pady=(4, 12))
        self.user = entry(self.inner, "Username", width=300)
        self.pw = entry(self.inner, "Password (min. 8 karakter)", show="•", width=300)
        self.pw2 = entry(self.inner, "Ulangi password", show="•", width=300)
        for w in (self.user, self.pw, self.pw2):
            w.pack(pady=4)
        row = ctk.CTkFrame(self.inner, fg_color="transparent")
        row.pack(pady=4)
        self.drive_var = ctk.StringVar()
        self.menu = ctk.CTkOptionMenu(row, variable=self.drive_var, values=["-"], width=220, height=36,
                                      fg_color=T.SOFT, button_color=T.PRIMARY, text_color=T.TEXT)
        self.menu.pack(side="left")
        secondary_button(row, "⟳", self._refresh, width=70).pack(side="left", padx=(8, 0))
        self.status = status_label(self.inner)
        self.status.configure(wraplength=320)
        self.status.pack(pady=6)
        primary_button(self.inner, "Daftar", self.do_register, width=300).pack(pady=3)
        secondary_button(self.inner, "Kembali", lambda: app.show("donggle"), width=300).pack(pady=3)
        label(self.inner, "⚠ Simpan donggle dengan aman. Lupa password = data tidak dapat dipulihkan.",
              11, color=T.WARNING, wraplength=320).pack(pady=(6, 0))
        self._refresh()

    def _refresh(self):
        d = donggle.list_removable_drives() or ["(tidak ada flashdisk)"]
        self.menu.configure(values=d)
        self.drive_var.set(d[0])

    def do_register(self):
        drive = self.drive_var.get()
        if drive.startswith("("):
            drive = ""
        try:
            uid = self.svc.auth.register(self.user.get(), self.pw.get(), self.pw2.get(), drive)
        except (AuthError, donggle.DonggleError) as e:
            set_status(self.status, f"✘ {e}", False)
            return
        self.svc.log("REGISTER", "OK", self.user.get().strip(), user_id=uid)
        self.app.notify("Registrasi berhasil. Silakan verifikasi donggle.", "success")
        self.app.show("donggle")


class LoginPage(_Center):
    def __init__(self, master, app):
        super().__init__(master, app)
        label(self.inner, "👤 Login", 22, "bold").pack()
        label(self.inner, "Donggle terverifikasi ✔", 12, color=T.SUCCESS).pack(pady=(4, 14))
        self.user = entry(self.inner, "Username", width=300)
        self.pw = entry(self.inner, "Password", show="•", width=300)
        self.user.pack(pady=4)
        self.pw.pack(pady=4)
        self.pw.bind("<Return>", lambda e: self.login())
        self.status = status_label(self.inner)
        self.status.configure(wraplength=300)
        self.status.pack(pady=6)
        primary_button(self.inner, "Masuk", self.login, width=300).pack(pady=3)
        secondary_button(self.inner, "Batal", lambda: app.show("donggle"), width=300).pack(pady=3)

    def login(self):
        try:
            name = self.svc.auth.login(self.user.get(), self.pw.get(), self.app.donggle_pub)
        except AuthError as e:
            self.svc.log("LOGIN_FAILED", "FAIL")
            set_status(self.status, f"✘ {e}", False)
            return
        self.svc.log("LOGIN", "OK", "password+donggle")
        self.app.notify(f"Selamat datang, {name}", "success")
        self.app.show("biometric")


class BiometricPage(_Center):
    def __init__(self, master, app):
        super().__init__(master, app)
        label(self.inner, "🖐 Windows Hello", 22, "bold").pack()
        label(self.inner, "Verifikasi identitas dengan sidik jari, wajah, atau PIN Windows.", 12,
              color=T.MUTED, wraplength=320).pack(pady=(4, 14))
        self.status = status_label(self.inner)
        self.status.configure(wraplength=320)
        self.status.pack(pady=6)
        self.btn = primary_button(self.inner, "Verifikasi dengan Windows Hello", self.start, width=300)
        self.btn.pack(pady=3)
        secondary_button(self.inner, "Batal", self.cancel, width=300).pack(pady=3)
        self._result = None

    def start(self):
        self.btn.configure(state="disabled")
        set_status(self.status, "Menunggu dialog Windows Hello...")
        self._result = None
        threading.Thread(target=self._worker, daemon=True).start()
        self.after(150, self._poll)

    def _worker(self):
        try:
            windows_hello.verify()
            self._result = (True, "")
        except windows_hello.HelloError as e:
            self._result = (False, str(e))

    def _poll(self):
        if self._result is None:
            self.after(150, self._poll)
            return
        ok, msg = self._result
        if ok:
            self.svc.log("BIOMETRIC", "OK", "windows_hello")
            self.app.show("shell")
        else:
            self.svc.log("BIOMETRIC", "FAIL")
            self.btn.configure(state="normal")
            set_status(self.status, f"✘ {msg}", False)

    def cancel(self):
        self.svc.auth.logout()
        self.app.show("donggle")
