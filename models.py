from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ArtBrief:
    concept: str
    description: str
    mood: str
    visual_elements: list[str]
    palette: list[str]
    style: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ArtBrief":
        return cls(
            concept=str(value["concept"]),
            description=str(value["description"]),
            mood=str(value["mood"]),
            visual_elements=[str(x) for x in value["visual_elements"]],
            palette=[str(x) for x in value["palette"]],
            style=str(value["style"]),
        )
