import pytest

from private_quant_terminal.brokers.errors import (
    BrokerAuthenticationError,
    BrokerConnectionError,
    BrokerError,
    BrokerNotFoundError,
    BrokerOrderError,
)


def test_broker_error_is_exception() -> None:
    error = BrokerError("Broker error")

    assert isinstance(error, Exception)
    assert str(error) == "Broker error"


@pytest.mark.parametrize(
    "error_class",
    [
        BrokerConnectionError,
        BrokerAuthenticationError,
        BrokerOrderError,
        BrokerNotFoundError,
    ],
)
def test_specific_broker_errors_inherit_from_broker_error(
    error_class: type[BrokerError],
) -> None:
    error = error_class("Test error")

    assert isinstance(error, BrokerError)
    assert isinstance(error, Exception)
    assert str(error) == "Test error"