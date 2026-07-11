"""Type-safe data provider capability declarations."""

from __future__ import annotations

from enum import StrEnum


class ProviderCapability(StrEnum):
    """Stable, serializable capability identifiers for data providers."""

    STOCK_BASIC = "stock_basic"
    TRADING_CALENDAR = "trading_calendar"
    DAILY_BAR = "daily_bar"
    MINUTE_BAR = "minute_bar"
    CORPORATE_ACTION = "corporate_action"
    FINANCIAL_STATEMENT = "financial_statement"
    INDEX_DAILY = "index_daily"
    ETF_DAILY = "etf_daily"
