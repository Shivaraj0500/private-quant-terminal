from private_quant_terminal.brokers.time_in_force import TimeInForce


def test_time_in_force_values() -> None:
    assert TimeInForce.DAY == "DAY"
    assert TimeInForce.GTC == "GTC"
    assert TimeInForce.IOC == "IOC"
    assert TimeInForce.FOK == "FOK"
