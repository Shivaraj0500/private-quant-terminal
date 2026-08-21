import pytest

from private_quant_terminal.data.streaming.base import LiveMarketDataProvider


def test_live_market_data_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        LiveMarketDataProvider()
