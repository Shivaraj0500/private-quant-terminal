import pytest

from private_quant_terminal.data.providers.broker_adapter import BrokerAdapter
from private_quant_terminal.models.market_depth import MarketDepth
from private_quant_terminal.models.quote import Quote
from private_quant_terminal.models.tick import Tick


class CompleteBrokerAdapter(BrokerAdapter):
    def get_quote(self, symbol: str) -> Quote:
        raise NotImplementedError

    def get_market_depth(self, symbol: str) -> MarketDepth:
        raise NotImplementedError

    def stream_ticks(self, symbols: list[str]) -> None:
        pass

    def subscribe_ticks(self, symbols: list[str]):
        if False:
            yield Tick

    def subscribe_quotes(self, symbols: list[str]):
        if False:
            yield Quote

    def subscribe_market_depth(self, symbols: list[str]):
        if False:
            yield MarketDepth

    def is_authenticated(self) -> bool:
        return False

    def authenticate(self) -> None:
        pass

    def disconnect(self) -> None:
        pass


def test_broker_adapter_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerAdapter()


def test_complete_broker_adapter_can_be_instantiated() -> None:
    provider = CompleteBrokerAdapter()

    assert isinstance(provider, BrokerAdapter)
    assert provider.is_authenticated() is False