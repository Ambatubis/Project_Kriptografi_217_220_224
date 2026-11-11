"""Hash chain lokal sederhana (BUKAN blockchain terdistribusi).

Keterbatasan: tidak ada konsensus/node lain. Pihak yang punya akses penuh ke
database dapat menghitung ulang seluruh rantai. Sistem ini mendeteksi
perubahan parsial/tidak sengaja, bukan penyerang yang menghitung ulang semua blok.
"""
from datetime import datetime
from .block import Block

GENESIS_PREV = "0" * 64


class Blockchain:
    def __init__(self, repo):
        self.repo = repo                 # BlockchainRepository
        if self.repo.count() == 0:
            self._add(Block(0, self._now(), "GENESIS BLOCK", GENESIS_PREV))

    @staticmethod
    def _now() -> str:
        return datetime.now().isoformat(timespec="seconds")

    def _add(self, block: Block) -> Block:
        block.current_hash = block.compute_hash()
        self.repo.insert(block)
        return block

    def add_block(self, data: str) -> Block:
        last = self.repo.last()
        return self._add(Block(last.index + 1, self._now(), data, last.current_hash))

    def blocks(self) -> list[Block]:
        return self.repo.all()

    def verify(self) -> tuple[bool, int | None, str]:
        """Return (valid, index_blok_bermasalah, pesan)."""
        prev = GENESIS_PREV
        for b in self.blocks():
            if b.previous_hash != prev:
                return False, b.index, f"Blok #{b.index}: previous_hash tidak cocok (rantai putus)."
            if b.compute_hash() != b.current_hash:
                return False, b.index, f"Blok #{b.index}: data diubah (hash tidak cocok)."
            prev = b.current_hash
        return True, None, "Blockchain valid: seluruh blok konsisten."
