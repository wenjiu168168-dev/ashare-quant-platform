from ashare_quant.utils.exceptions import (
    AShareQuantError,
    ConfigurationError,
    DataQualityError,
    TimeAlignmentError,
)


def test_project_exceptions_share_base_class() -> None:
    assert issubclass(ConfigurationError, AShareQuantError)
    assert issubclass(DataQualityError, AShareQuantError)
    assert issubclass(TimeAlignmentError, AShareQuantError)
