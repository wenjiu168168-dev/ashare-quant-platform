import pytest

from ashare_quant.data.provider.base import BaseDataProvider
from ashare_quant.data.provider.capabilities import ProviderCapability
from ashare_quant.data.provider.exceptions import (
    ProviderAlreadyRegisteredError,
    ProviderNotFoundError,
)
from ashare_quant.data.provider.registry import ProviderRegistry
from ashare_quant.data.provider.types import ProviderHealth, ProviderHealthStatus


class RegistryDummyProvider(BaseDataProvider):
    def __init__(self, provider_id: str) -> None:
        self._provider_id = provider_id

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def display_name(self) -> str:
        return f"Provider {self._provider_id}"

    @property
    def capabilities(self) -> frozenset[ProviderCapability]:
        return frozenset({ProviderCapability.TRADING_CALENDAR})

    def health_check(self) -> ProviderHealth:
        return ProviderHealth(provider_id=self.provider_id, status=ProviderHealthStatus.HEALTHY)


def test_registry_registers_and_gets_provider() -> None:
    registry = ProviderRegistry()
    provider = RegistryDummyProvider("provider_b")

    registry.register(provider)

    assert registry.contains("provider_b")
    assert registry.get("provider_b") is provider


def test_registry_unregisters_provider() -> None:
    registry = ProviderRegistry()
    provider = RegistryDummyProvider("provider_b")
    registry.register(provider)

    registry.unregister("provider_b")

    assert not registry.contains("provider_b")
    with pytest.raises(ProviderNotFoundError):
        registry.get("provider_b")


def test_registry_rejects_duplicate_provider_id() -> None:
    registry = ProviderRegistry()
    registry.register(RegistryDummyProvider("provider_b"))

    with pytest.raises(ProviderAlreadyRegisteredError):
        registry.register(RegistryDummyProvider("provider_b"))


def test_registry_get_missing_provider_raises() -> None:
    registry = ProviderRegistry()

    with pytest.raises(ProviderNotFoundError):
        registry.get("missing")


def test_registry_unregister_missing_provider_raises() -> None:
    registry = ProviderRegistry()

    with pytest.raises(ProviderNotFoundError):
        registry.unregister("missing")


def test_registry_returns_stable_sorted_provider_ids() -> None:
    registry = ProviderRegistry()
    registry.register(RegistryDummyProvider("provider_c"))
    registry.register(RegistryDummyProvider("provider_a"))
    registry.register(RegistryDummyProvider("provider_b"))

    assert registry.list_provider_ids() == ("provider_a", "provider_b", "provider_c")


def test_registry_provider_snapshot_cannot_mutate_internal_state() -> None:
    registry = ProviderRegistry()
    registry.register(RegistryDummyProvider("provider_b"))

    providers = registry.list_providers()

    assert len(providers) == 1
    assert isinstance(providers, tuple)
    with pytest.raises(AttributeError):
        providers.clear()  # type: ignore[attr-defined]
    assert registry.contains("provider_b")


def test_registry_clear_removes_all_providers() -> None:
    registry = ProviderRegistry()
    registry.register(RegistryDummyProvider("provider_b"))

    registry.clear()

    assert registry.list_provider_ids() == ()
