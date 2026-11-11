import customtkinter as ctk
from ui import theme as T
from ui.widgets import (Page, card, label, primary_button, secondary_button, status_label, set_status,
                        make_table, textbox, set_text)


class BlockchainPage(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.header("Blockchain Explorer", "Hash chain lokal SHA-256 (bukan blockchain terdistribusi). "
                    "Mendeteksi perubahan data pada blok.")
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=28, pady=6)
        primary_button(row, "✔ Verifikasi Integritas", self.verify, width=210).pack(side="left")
        secondary_button(row, "⟳ Muat Ulang", self.reload, width=130).pack(side="left", padx=8)
        self.status = status_label(row)
        self.status.configure(wraplength=500)
        self.status.pack(side="left", padx=12)
        frame, self.tree = make_table(self, [("i", "#", 45), ("t", "Timestamp", 150), ("d", "Data", 330),
                                             ("p", "Previous Hash", 130), ("h", "Current Hash", 130)])
        frame.pack(fill="both", expand=True, padx=28, pady=6)
        self.detail = textbox(self, 90)
        self.detail.pack(fill="x", padx=28, pady=(0, 20))
        self.tree.bind("<<TreeviewSelect>>", self.show_detail)
        self.reload()

    def reload(self):
        self.tree.delete(*self.tree.get_children())
        self.blocks = {b.index: b for b in self.svc.chain.blocks()}
        for b in self.blocks.values():
            self.tree.insert("", "end", values=(b.index, b.timestamp, b.data[:60], b.previous_hash[:14] + "…",
                                                b.current_hash[:14] + "…"))

    def show_detail(self, _=None):
        sel = self.tree.selection()
        if sel:
            b = self.blocks[int(self.tree.item(sel[0])["values"][0])]
            set_text(self.detail, f"Index: {b.index}\nTimestamp: {b.timestamp}\nData: {b.data}\n"
                                  f"Previous: {b.previous_hash}\nCurrent : {b.current_hash}")

    def verify(self):
        ok, idx, msg = self.svc.chain.verify()
        set_status(self.status, ("✔ " if ok else "✘ ") + msg, ok)
        self.app.notify(msg, "success" if ok else "error")
        if not ok:
            for item in self.tree.get_children():
                if int(self.tree.item(item)["values"][0]) == idx:
                    self.tree.selection_set(item)
                    self.tree.see(item)
