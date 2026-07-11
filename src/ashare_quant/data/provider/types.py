"""Minimal provider-layer types."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from types import MappingProxyType


class ProviderHealthStatus(StrEnum):
    """Standard health states for a data provider."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    """Structured health-check result for a data provider."""

    provider_id: str
    status: ProviderHealthStatus
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    message: str = ""
    latency_ms: float | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate timezone awareness and protect metadata from mutation."""

        if self.checked_at.tzinfo is None or self.checked_at.utcoffset() is None:
            raise ValueError("ProviderHealth.checked_at must be timezone-aware")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
