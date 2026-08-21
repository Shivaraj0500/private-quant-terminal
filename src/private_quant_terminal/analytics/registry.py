"""Registry for technical analysis indicators."""

from typing import Any


class IndicatorRegistry:
    """Store and retrieve technical analysis indicators by name."""

    def __init__(self) -> None:
        self._indicators: dict[str, Any] = {}

    def register(self, name: str, indicator: Any) -> None:
        """Register an indicator."""

        if not name:
            raise ValueError("Indicator name cannot be empty.")

        if name in self._indicators:
            raise ValueError(f"Indicator already registered: {name}")

        self._indicators[name] = indicator

    def get(self, name: str) -> Any:
        """Return a registered indicator."""

        try:
            return self._indicators[name]
        except KeyError as exc:
            raise KeyError(f"Unknown indicator: {name}") from exc

    def names(self) -> list[str]:
        """Return registered indicator names in alphabetical order."""

        return sorted(self._indicators)