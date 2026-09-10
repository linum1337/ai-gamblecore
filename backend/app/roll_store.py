import time
from dataclasses import dataclass
from threading import Lock

from app.schemas import RollItem


@dataclass
class StoredRoll:
    rolls: list[RollItem]
    expires_at: float


class RollStore:
    def __init__(self) -> None:
        self._items: dict[str, StoredRoll] = {}
        self._lock = Lock()

    def put(self, roll_id: str, rolls: list[RollItem], ttl: int) -> None:
        now = time.monotonic()
        with self._lock:
            self._purge(now)
            self._items[roll_id] = StoredRoll(rolls=rolls, expires_at=now + ttl)

    def consume(self, roll_id: str) -> list[RollItem] | None:
        now = time.monotonic()
        with self._lock:
            self._purge(now)
            item = self._items.pop(roll_id, None)
        return item.rolls if item else None

    def _purge(self, now: float) -> None:
        expired = [key for key, item in self._items.items() if item.expires_at <= now]
        for key in expired:
            self._items.pop(key, None)

