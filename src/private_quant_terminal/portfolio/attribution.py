from dataclasses import dataclass


@dataclass(frozen=True)
class Attribution:
    """Return attribution for a single portfolio position."""

    symbol: str
    pnl: float
    contribution: float


def calculate_attribution(
    pnl_by_symbol: dict[str, float],
) -> tuple[Attribution, ...]:
    """Calculate each symbol's contribution to total portfolio P&L."""

    total_pnl = sum(pnl_by_symbol.values())

    if total_pnl == 0:
        return tuple(
            Attribution(
                symbol=symbol,
                pnl=pnl,
                contribution=0.0,
            )
            for symbol, pnl in pnl_by_symbol.items()
        )

    return tuple(
        Attribution(
            symbol=symbol,
            pnl=pnl,
            contribution=(pnl / total_pnl) * 100.0,
        )
        for symbol, pnl in pnl_by_symbol.items()
    )