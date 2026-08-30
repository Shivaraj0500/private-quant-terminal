from collections.abc import AsyncIterator

import pytest

from private_quant_terminal.data.providers.broker_adapter import BrokerAdapter
from private_quant_terminal.models.market_depth import MarketDepth
from private_quant_terminal.models.quote import Quote
from private_quant_terminal.models.tick import Tick


class CompleteBrokerAdapter(BrokerAdapter):
    """Concrete implementation used for testing BrokerAdapter."""

    def is_authenticated(self) -> bool:
        return True

    def authenticate(self) -> None:
        return None

    def disconnect(self) -> None:
        return None

    def get_quote(self, symbol: str) -> Quote:
        raise NotImplementedError

    def get_market_depth(self, symbol: str) -> MarketDepth:
        raise NotImplementedError

    def stream_ticks(self, symbols: list[str]) -> None:
        return None

    async def subscribe_ticks(
        self,
        symbols: list[str],
    ) -> AsyncIterator[Tick]:
        if False:
            yield

    async def subscribe_quotes(
        self,
        symbols: list[str],
    ) -> AsyncIterator[Quote]:
        if False:
            yield

    async def subscribe_market_depth(
        self,
        symbols: list[str],
    ) -> AsyncIterator[MarketDepth]:
        if False:
            yield


class TestBrokerAdapter:
    def test_broker_adapter_is_abstract(self) -> None:
        """BrokerAdapter itself cannot be instantiated."""
        with pytest.raises(TypeError):
            BrokerAdapter()

    def test_complete_broker_adapter_can_be_instantiated(self) -> None:
        """A complete implementation can be instantiated."""
        adapter = CompleteBrokerAdapter()

        assert isinstance(adapter, BrokerAdapter)

    def test_complete_broker_adapter_is_authenticated(self) -> None:
        """Concrete implementation returns authentication status."""
        adapter = CompleteBrokerAdapter()

        assert adapter.is_authenticated() is True

    def test_complete_broker_adapter_authenticate(self) -> None:
        """Concrete implementation can authenticate."""
        adapter = CompleteBrokerAdapter()

        result = adapter.authenticate()

        assert result is None

    def test_complete_broker_adapter_disconnect(self) -> None:
        """Concrete implementation can disconnect."""
        adapter = CompleteBrokerAdapter()

        result = adapter.disconnect()

        assert result is None

    def test_abstract_is_authenticated_body_raises_not_implemented(self) -> None:
        """Cover the default abstract method body."""
        with pytest.raises(NotImplementedError):
            BrokerAdapter.is_authenticated(None)

    def test_abstract_authenticate_body_raises_not_implemented(self) -> None:
        """Cover the default abstract method body."""
        with pytest.raises(NotImplementedError):
            BrokerAdapter.authenticate(None)

    def test_abstract_disconnect_body_raises_not_implemented(self) -> None:
        """Cover the default abstract method body."""
        with pytest.raises(NotImplementedError):
            BrokerAdapter.disconnect(None)