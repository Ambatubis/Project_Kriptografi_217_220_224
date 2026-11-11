"""Tema: Modern Minimalist - White & Blue."""
from tkinter import ttk
import customtkinter as ctk

PRIMARY = "#1E6FF0"
PRIMARY_HOVER = "#1559C7"
BG = "#F5F8FC"
CARD = "#FFFFFF"
BORDER = "#E1E8F2"
SOFT = "#EAF1FD"
TEXT = "#16233A"
MUTED = "#6B7A90"
SUCCESS = "#16A34A"
DANGER = "#DC2626"
WARNING = "#D97706"

FONT = "Segoe UI"


def font(size=13, weight="normal"):
    return ctk.CTkFont(family=FONT, size=size, weight=weight)


def init_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    st = ttk.Style()
    st.theme_use("clam")
    st.configure("Treeview", rowheight=28, font=(FONT, 10), background="white",
                 fieldbackground="white", borderwidth=0, foreground=TEXT)
    st.configure("Treeview.Heading", font=(FONT, 10, "bold"), background=SOFT,
                 foreground=TEXT, relief="flat")
    st.map("Treeview", background=[("selected", PRIMARY)], foreground=[("selected", "white")])
