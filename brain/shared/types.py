"""Value Objects — Shared Kernel

Unveraenderliche Wert-Objekte die von allen Bounded Contexts genutzt werden.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List


@dataclass(frozen=True)
class Embedding:
    """384-dimensionaler Vektor. Unveraenderliches Value Object."""
    values: tuple

    def to_list(self) -> List[float]:
        return list(self.values)

    @classmethod
    def from_list(cls, values: List[float]) -> Embedding:
        return cls(values=tuple(values))


@dataclass(frozen=True)
class Timestamp:
    """UTC Zeitstempel. Unveraenderliches Value Object."""
    value: datetime

    @classmethod
    def now(cls) -> Timestamp:
        return cls(value=datetime.now(timezone.utc))

    def isoformat(self) -> str:
        return self.value.isoformat()

    @classmethod
    def from_iso(cls, iso_str: str) -> Timestamp:
        return cls(value=datetime.fromisoformat(iso_str))


@dataclass(frozen=True)
class Score:
    """Aehnlichkeits- oder Relevanz-Score 0.0-1.0."""
    value: float

    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            object.__setattr__(self, 'value', max(0.0, min(1.0, self.value)))

    def __float__(self) -> float:
        return self.value
