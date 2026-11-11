import hashlib
from dataclasses import dataclass


@dataclass
class Block:
    index: int
    timestamp: str
    data: str
    previous_hash: str
    current_hash: str = ""

    def compute_hash(self) -> str:
        raw = f"{self.index}|{self.timestamp}|{self.data}|{self.previous_hash}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
