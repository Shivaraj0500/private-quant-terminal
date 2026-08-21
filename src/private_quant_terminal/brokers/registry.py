from .base import Strategy


class StrategyRegistry:
    """Registry for trading strategies."""

    def __init__(self) -> None:
        self._strategies: dict[str, Strategy] = {}

    def register(self, strategy: Strategy) -> None:
        """Register a strategy."""
        name = strategy.name

        if name in self._strategies:
            raise ValueError(
                f"Strategy already registered: {name}"
            )

        self._strategies[name] = strategy

    def get(self, name: str) -> Strategy:
        """Get a strategy by name."""
        try:
            return self._strategies[name]
        except KeyError as exc:
            raise KeyError(
                f"Strategy not found: {name}"
            ) from exc

    def names(self) -> list[str]:
        """Return registered strategy names."""
        return list(self._strategies.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._strategies