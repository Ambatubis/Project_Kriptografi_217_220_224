"""Komponen UI yang dipakai ulang."""
from tkinter import ttk
import customtkinter as ctk
from ui import theme as T


def card(parent, **kw):
    return ctk.CTkFrame(parent, fg_color=T.CARD, corner_radius=14, border_width=1, border_color=T.BORDER, **kw)


def label(parent, text, size=13, weight="normal", color=T.TEXT, **kw):
    return ctk.CTkLabel(parent, text=text, font=T.font(size, weight), text_color=color, **kw)


def primary_button(parent, text, command, width=160, **kw):
    return ctk.CTkButton(parent, text=text, command=command, width=width, height=38, corner_radius=10,
                         fg_color=T.PRIMARY, hover_color=T.PRIMARY_HOVER, font=T.font(13, "bold"), **kw)


def secondary_button(parent, text, command, width=140, **kw):
    return ctk.CTkButton(parent, text=text, command=command, width=width, height=38, corner_radius=10,
                         fg_color=T.SOFT, hover_color="#D6E4FB", text_color=T.PRIMARY,
                         font=T.font(13, "bold"), **kw)


def danger_button(parent, text, command, width=120, **kw):
    return ctk.CTkButton(parent, text=text, command=command, width=width, height=38, corner_radius=10,
                         fg_color="#FDECEC", hover_color="#F9D2D2", text_color=T.DANGER,
                         font=T.font(13, "bold"), **kw)


def entry(parent, placeholder="", show=None, **kw):
    return ctk.CTkEntry(parent, placeholder_text=placeholder, show=show, height=38, corner_radius=10,
                        border_color=T.BORDER, fg_color="white", text_color=T.TEXT, font=T.font(13), **kw)


def textbox(parent, height=120, **kw):
    return ctk.CTkTextbox(parent, height=height, corner_radius=10, border_width=1, border_color=T.BORDER,
                          fg_color="white", text_color=T.TEXT, font=T.font(13), **kw)


def status_label(parent):
    return label(parent, "", 12, color=T.MUTED, anchor="w", justify="left", wraplength=700)


def set_status(lbl, text, ok=None):
    color = T.MUTED if ok is None else (T.SUCCESS if ok else T.DANGER)
    lbl.configure(text=text, text_color=color)


def make_table(parent, columns):
    """columns: [(id, judul, lebar)]. Return (frame, tree)."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show="headings", selectmode="browse")
    for cid, head, w in columns:
        tree.heading(cid, text=head)
        tree.column(cid, width=w, anchor="w")
    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    sb.grid(row=0, column=1, sticky="ns")
    return frame, tree


def get_text(tb) -> str:
    return tb.get("1.0", "end-1c")


def set_text(tb, text: str):
    tb.delete("1.0", "end")
    tb.insert("1.0", text)


class Page(ctk.CTkFrame):
    """Dasar halaman: punya akses ke app & services."""
    def __init__(self, master, app):
        super().__init__(master, fg_color=T.BG)
        self.app, self.svc = app, app.svc

    def header(self, title, subtitle=""):
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.pack(fill="x", padx=28, pady=(24, 8))
        label(box, title, 24, "bold").pack(anchor="w")
        if subtitle:
            label(box, subtitle, 13, color=T.MUTED, anchor="w", justify="left", wraplength=800).pack(anchor="w")
        return box
