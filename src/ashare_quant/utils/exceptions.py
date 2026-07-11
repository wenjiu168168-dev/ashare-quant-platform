"""Project-wide exception hierarchy."""


class AShareQuantError(Exception):
    """Base exception for all project-specific errors."""


class ConfigurationError(AShareQuantError):
    """Raised when configuration loading or validation fails."""


class DataQualityError(AShareQuantError):
    """Raised when data quality checks fail in future data modules."""


class TimeAlignmentError(AShareQuantError):
    """Raised when signal, data, or trading timestamps are inconsistent."""
