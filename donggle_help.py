from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk


def show_dongle_help(parent: tk.Misc, local_dongle_path: Path, external_dongle_path: Path) -> None:
    """Display the dongle usage guide in a separate window."""
    window = tk.Toplevel(parent)
    window.title("Bantuan Dongle")
    window.geometry("520x340")
    window.resizable(False, False)
    window.transient(parent)
    window.grab_set()

    frame = ttk.Frame(window, padding=16)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Panduan penggunaan dongle vault", font=("", 12, "bold")).pack(anchor="w")

    info = tk.Text(frame, wrap="word", height=12, width=58, state="normal")
    info.insert(
        "1.0",
        "1. Saat pendaftaran, aplikasi membuat file dongle lokal di:\n"
        f"{local_dongle_path}\n\n"
        "2. Untuk mode drive eksternal, salin file tersebut ke:\n"
        f"{external_dongle_path}\n\n"
        "3. Saat login, aplikasi akan membaca dongle dari drive eksternal jika tersedia; "
        "jika tidak ada, akan memakai fallback lokal.\n\n"
        "4. Jika file dongle diubah, hilang, atau tidak cocok, login otomatis ditolak.\n\n"
        "5. File ini berfungsi sebagai verifikasi tambahan yang ringan, bukan pengganti keamanan fisik yang sesungguhnya.",
    )
    info.configure(state="disabled")
    info.pack(fill="both", expand=True, pady=(8, 10))

    ttk.Button(frame, text="Tutup", command=window.destroy).pack(anchor="e")
