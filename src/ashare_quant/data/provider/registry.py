"""Provider registry implementation."""

from __future__ import annotations

from collections.abc import Sequence

from ashare_quant.data.provider.base import BaseDataProvider
from ashare_quant.data.provider.exceptions import (
    ProviderAlreadyRegisteredError,
    ProviderNotFoundError,
)


class ProviderRegistry:
    """Instance-based registry for data providers.

    The first version is intentionally not thread-safe. Create separate registry instances
    for tests or dependency-injected application contexts to avoid shared mutable state.
    """

    def __init__(self) -> None:
        self._providers: dict[str, BaseDataProvider] = {}

    def register(self, provider: BaseDataProvider) -> None:
        """Register a provider instance by its stable provider ID."""

        provider_id = provider.provider_id
        if provider_id in self._providers:
            raise ProviderAlreadyRegisteredError(provider_id)
        self._providers[provider_id] = provider

    def unregister(self, provider_id: str) -> None:
        """Unregister a provider by ID."""

        if provider_id not in self._providers:
            raise ProviderNotFoundError(provider_id)
        del self._providers[provider_id]

    def get(self, provider_id: str) -> BaseDataProvider:
        """Return a registered provider by ID."""

        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise ProviderNotFoundError(provider_id) from exc

    def contains(self, provider_id: str) -> bool:
        """Return whether a provider ID is registered."""

        return provider_id in self._providers

    def list_provider_ids(self) -> tuple[str, ...]:
        """Return registered provider IDs in stable sorted order."""

        return tuple(sorted(self._providers))

    def list_providers(self) -> Sequence[BaseDataProvider]:
        """Return an immutable snapshot of registered provider instances."""

        return tuple(self._providers[provider_id] for provider_id in self.list_provider_ids())

    def clear(self) -> None:
        """Remove all providers from this registry."""

        self._providers.clear()
