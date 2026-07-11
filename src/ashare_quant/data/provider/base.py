"""Abstract base class for data providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

from ashare_quant.data.provider.capabilities import ProviderCapability
from ashare_quant.data.provider.types import ProviderHealth


class BaseDataProvider(ABC):
    """Minimal interface boundary for data provider implementations."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Return a stable, unique, machine-readable provider identifier."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Return a human-readable provider name."""

    @property
    @abstractmethod
    def capabilities(self) -> frozenset[ProviderCapability]:
        """Return the immutable set of capabilities supported by this provider."""

    def supports(self, capability: ProviderCapability) -> bool:
        """Return whether this provider supports a capability."""

        return capability in self.capabilities

    @abstractmethod
    def health_check(self) -> ProviderHealth:
        """Return a structured provider health result."""

    def close(self) -> None:
        """Release provider resources.

        Providers without external resources may keep this default no-op implementation.
        """

        return None

    def __enter__(self) -> Self:
        """Enter a provider context manager."""

        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Exit a provider context manager and release resources."""

        self.close()
