import pytest

from private_quant_terminal.data.providers.base import MarketDataProvider


class TestMarketDataProvider:
    def test_provider_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            MarketDataProvider()

    def test_get_instrument_body_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            MarketDataProvider.get_instrument(
                None,
                "NIFTY",
            )

    def test_get_candles_body_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            MarketDataProvider.get_candles(
                None,
                "NIFTY",
                "1d",
                10,
            )