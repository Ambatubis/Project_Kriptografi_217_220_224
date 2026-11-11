"""Jendela utama dan navigasi antar halaman."""
import customtkinter as ctk
from core import config
from core.services import Services
from ui import theme as T


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        T.init_theme()
        self.title(f"{config.APP_NAME}: Brankas Digital")
        self.geometry("1150x720")
        self.minsize(960, 620)
        self.configure(fg_color=T.BG)
        self.svc = Services()
        self.donggle_pub = None
        self._toast = None
        self._page = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.show("splash")

    def show(self, name: str):
        from ui.pages_auth import SplashPage, DonggleVerifyPage, RegisterPage, LoginPage, BiometricPage
        from ui.shell import Shell
        # Gerbang akses: halaman setelah login hanya boleh dibuka jika semua lapis lolos
        if name == "login" and self.donggle_pub is None:
            name = "donggle"
        if name == "biometric" and not self.svc.session.active:
            name = "donggle"
        if name == "shell" and not self.svc.session.active:
            name = "donggle"
        pages = {"splash": SplashPage, "donggle": DonggleVerifyPage, "register": RegisterPage,
                 "login": LoginPage, "biometric": BiometricPage, "shell": Shell}
        if self._page is not None:
            self._page.destroy()
        self._page = pages[name](self, self)
        self._page.grid(row=0, column=0, sticky="nsew")

    def notify(self, message: str, kind: str = "info"):
        colors = {"success": T.SUCCESS, "error": T.DANGER, "info": T.PRIMARY}
        if self._toast is not None:
            self._toast.destroy()
        self._toast = ctk.CTkLabel(self, text=f"  {message}  ", font=T.font(13, "bold"), text_color="white",
                                   fg_color=colors.get(kind, T.PRIMARY), corner_radius=10, height=40)
        self._toast.place(relx=1.0, rely=0.0, x=-24, y=20, anchor="ne")
        toast = self._toast
        self.after(3500, lambda: toast.destroy() if toast.winfo_exists() else None)

    def _close(self):
        self.svc.auth.logout()
        self.svc.db.close()
        self.destroy()
