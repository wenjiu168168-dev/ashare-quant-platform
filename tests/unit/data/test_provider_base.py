from datetime import UTC, datetime

import pytest

from ashare_quant.data.provider.base import BaseDataProvider
from ashare_quant.data.provider.capabilities import ProviderCapability
from ashare_quant.data.provider.types import ProviderHealth, ProviderHealthStatus


class DummyDataProvider(BaseDataProvider):
    def __init__(self) -> None:
        self.closed = False

    @property
    def provider_id(self) -> str:
        return "dummy"

    @property
    def display_name(self) -> str:
        return "Dummy Data Provider"

    @property
    def capabilities(self) -> frozenset[ProviderCapability]:
        return frozenset({ProviderCapability.STOCK_BASIC, ProviderCapability.DAILY_BAR})

    def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider_id=self.provider_id,
            status=ProviderHealthStatus.HEALTHY,
            checked_at=datetime.now(UTC),
            message="dummy provider is healthy",
        )

    def close(self) -> None:
        self.closed = True


def test_base_data_provider_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        BaseDataProvider()


def test_dummy_provider_identity_and_capabilities() -> None:
    provider = DummyDataProvider()

    assert provider.provider_id == "dummy"
    assert provider.display_name == "Dummy Data Provider"
    assert provider.capabilities == frozenset(
        {ProviderCapability.STOCK_BASIC, ProviderCapability.DAILY_BAR}
    )


def test_supports_returns_expected_results() -> None:
    provider = DummyDataProvider()

    assert provider.supports(ProviderCapability.STOCK_BASIC)
    assert not provider.supports(ProviderCapability.MINUTE_BAR)


def test_health_check_returns_timezone_aware_provider_health() -> None:
    provider = DummyDataProvider()

    health = provider.health_check()

    assert isinstance(health, ProviderHealth)
    assert health.provider_id == "dummy"
    assert health.status is ProviderHealthStatus.HEALTHY
    assert health.checked_at.tzinfo is not None
    assert health.checked_at.utcoffset() is not None


def test_provider_health_rejects_naive_datetime() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ProviderHealth(
            provider_id="dummy",
            status=ProviderHealthStatus.UNKNOWN,
            checked_at=datetime(2026, 1, 1),
        )


def test_provider_health_metadata_is_immutable_snapshot() -> None:
    source_metadata: dict[str, object] = {"source": "unit-test"}

    health = ProviderHealth(
        provider_id="dummy",
        status=ProviderHealthStatus.HEALTHY,
        metadata=source_metadata,
    )
    source_metadata["source"] = "changed"

    assert health.metadata["source"] == "unit-test"
    with pytest.raises(TypeError):
        health.metadata["new"] = "value"  # type: ignore[index]


def test_context_manager_calls_close() -> None:
    provider = DummyDataProvider()

    with provider as active_provider:
        assert active_provider is provider
        assert not provider.closed

    assert provider.closed
