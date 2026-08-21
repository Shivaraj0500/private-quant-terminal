
import pytest

from private_quant_terminal.data.streaming.base import LiveMarketDataProvider


def test_live_market_data_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        LiveMarketDataProvider()


def test_incomplete_live_market_data_provider_is_abstract() -> None:
    class IncompleteProvider(LiveMarketDataProvider):
        pass

    with pytest.raises(TypeError):
        IncompleteProvider()


def test_complete_live_market_data_provider_can_be_instantiated() -> None:
    class CompleteProvider(LiveMarketDataProvider):
        async def connect(self) -> None:
            pass

        async def disconnect(self) -> None:
            pass

        def is_connected(self) -> bool:
            return False

        async def subscribe_ticks(self, symbols: list[str]):
            if False:
                yield None

        async def subscribe_quotes(self, symbols: list[str]):
            if False:
                yield None

        async def subscribe_market_depth(self, symbols: list[str]):
            if False:
                yield None

    provider = CompleteProvider()

    assert isinstance(provider, LiveMarketDataProvider)
    assert provider.is_connected() is False