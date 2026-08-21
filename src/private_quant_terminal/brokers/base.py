from abc import ABC, abstractmethod

from private_quant_terminal.strategies.signal import Signal


class Broker(ABC):
    """Base contract for all broker implementations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the broker name."""
        raise NotImplementedError

    @abstractmethod
    def execute_signal(self, signal: Signal) -> None:
        """Execute a trading signal."""
        raise NotImplementedError