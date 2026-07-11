"""Data provider exception hierarchy."""

from __future__ import annotations

from ashare_quant.utils.exceptions import AShareQuantError


class DataProviderError(AShareQuantError):
    """Base exception for provider-layer failures."""


class ProviderNotFoundError(DataProviderError):
    """Raised when a provider ID is not registered."""

    def __init__(self, provider_id: str) -> None:
        super().__init__(f"Data provider not found: provider_id={provider_id!r}")
        self.provider_id = provider_id


class ProviderAlreadyRegisteredError(DataProviderError):
    """Raised when registering a duplicate provider ID."""

    def __init__(self, provider_id: str) -> None:
        super().__init__(f"Data provider already registered: provider_id={provider_id!r}")
        self.provider_id = provider_id


class ProviderUnavailableError(DataProviderError):
    """Raised when a provider is unavailable for a requested operation."""

    def __init__(self, provider_id: str, reason: str) -> None:
        super().__init__(f"Data provider unavailable: provider_id={provider_id!r}, reason={reason}")
        self.provider_id = provider_id
        self.reason = reason


class UnsupportedCapabilityError(DataProviderError):
    """Raised when a provider does not support a required capability."""

    def __init__(self, provider_id: str, capability: object) -> None:
        super().__init__(
            f"Data provider does not support capability: "
            f"provider_id={provider_id!r}, capability={capability!r}"
        )
        self.provider_id = provider_id
        self.capability = capability


class ProviderConfigurationError(DataProviderError):
    """Raised when provider configuration is invalid."""

    def __init__(self, provider_id: str, message: str) -> None:
        super().__init__(f"Invalid provider configuration: provider_id={provider_id!r}, {message}")
        self.provider_id = provider_id
