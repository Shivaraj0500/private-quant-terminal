from dataclasses import dataclass

from private_quant_terminal.brokers.order_request import OrderRequest


@dataclass(frozen=True)
class ExecutionResult:
    """Result of converting a trading signal into an executable order."""

    signal_symbol: str
    order_request: OrderRequest | None
    executed: bool
    reason: str | None = None
