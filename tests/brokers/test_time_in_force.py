import pytest

from private_quant_terminal.brokers.time_in_force import TimeInForce


def test_time_in_force_values() -> None:
    assert TimeInForce.DAY == "DAY"
    assert TimeInForce.GTC == "GTC"
    assert TimeInForce.IOC == "IOC"
    assert TimeInForce.FOK == "FOK"


def test_time_in_force_member_values() -> None:
    assert TimeInForce.DAY.value == "DAY"
    assert TimeInForce.GTC.value == "GTC"
    assert TimeInForce.IOC.value == "IOC"
    assert TimeInForce.FOK.value == "FOK"


def test_time_in_force_can_be_created_from_valid_value() -> None:
    assert TimeInForce("DAY") is TimeInForce.DAY
    assert TimeInForce("GTC") is TimeInForce.GTC
    assert TimeInForce("IOC") is TimeInForce.IOC
    assert TimeInForce("FOK") is TimeInForce.FOK


def test_time_in_force_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        TimeInForce("INVALID")