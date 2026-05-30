from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderResponse:
    data: Any = None
    raw_payload: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    is_partial: bool = False


class BaseProvider(ABC):
    @abstractmethod
    def fetch(self, filters: dict[str, Any]) -> ProviderResponse:
        raise NotImplementedError
