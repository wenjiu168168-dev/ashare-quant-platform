from ashare_quant.data.provider.capabilities import ProviderCapability
from ashare_quant.data.provider.exceptions import (
    DataProviderError,
    ProviderAlreadyRegisteredError,
    ProviderConfigurationError,
    ProviderNotFoundError,
    ProviderUnavailableError,
    UnsupportedCapabilityError,
)
from ashare_quant.data.provider.types import ProviderHealthStatus
from ashare_quant.utils.exceptions import AShareQuantError


def test_provider_capability_values_are_stable_strings() -> None:
    assert ProviderCapability.STOCK_BASIC.value == "stock_basic"
    assert ProviderCapability.TRADING_CALENDAR.value == "trading_calendar"
    assert ProviderCapability.DAILY_BAR.value == "daily_bar"
    assert ProviderCapability.MINUTE_BAR.value == "minute_bar"
    assert ProviderCapability.CORPORATE_ACTION.value == "corporate_action"
    assert ProviderCapability.FINANCIAL_STATEMENT.value == "financial_statement"
    assert ProviderCapability.INDEX_DAILY.value == "index_daily"
    assert ProviderCapability.ETF_DAILY.value == "etf_daily"


def test_provider_capability_can_be_used_in_sets() -> None:
    capabilities = {ProviderCapability.STOCK_BASIC, ProviderCapability.DAILY_BAR}

    assert ProviderCapability.STOCK_BASIC in capabilities
    assert ProviderCapability.MINUTE_BAR not in capabilities


def test_provider_health_status_values_are_stable_strings() -> None:
    assert ProviderHealthStatus.HEALTHY.value == "healthy"
    assert ProviderHealthStatus.DEGRADED.value == "degraded"
    assert ProviderHealthStatus.UNAVAILABLE.value == "unavailable"
    assert ProviderHealthStatus.UNKNOWN.value == "unknown"


def test_provider_exceptions_inherit_project_base_exception() -> None:
    exception_types = (
        DataProviderError,
        ProviderNotFoundError,
        ProviderAlreadyRegisteredError,
        ProviderUnavailableError,
        UnsupportedCapabilityError,
        ProviderConfigurationError,
    )

    for exception_type in exception_types:
        assert issubclass(exception_type, AShareQuantError)
