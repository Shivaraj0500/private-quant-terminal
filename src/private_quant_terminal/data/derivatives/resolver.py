from __future__ import annotations

from datetime import datetime

from private_quant_terminal.data.derivatives.models import (
    HistoricalOptionChainSnapshot,
    HistoricalOptionContract,
)
from private_quant_terminal.models.instrument import (
    Instrument,
    InstrumentType,
    OptionType,
)
from private_quant_terminal.strategy.options import (
    ExpirySelection,
    OptionSelector,
    StrikeSelection,
)


class HistoricalOptionContractResolver:
    """Resolve declarative option selectors against a historical chain."""

    def resolve(
        self,
        selector: OptionSelector,
        chain: HistoricalOptionChainSnapshot,
        *,
        as_of: datetime,
    ) -> HistoricalOptionContract:
        self._validate_as_of(chain, as_of)

        if selector.underlying != chain.underlying:
            raise ValueError(
                "Option selector underlying does not match chain snapshot."
            )

        if selector.strike_selection is StrikeSelection.OFFSET:
            raise NotImplementedError(
                "OFFSET strike selection semantics are not defined."
            )

        quotes = tuple(
            quote
            for quote in chain.quotes
            if quote.contract.instrument.option_type is not None
            and quote.contract.instrument.option_type.value
            == selector.option_type.value
        )

        if not quotes:
            raise ValueError(
                "No historical option contracts match the requested option type."
            )

        expiry = self._resolve_expiry(selector, quotes, as_of)

        expiry_quotes = tuple(
            quote
            for quote in quotes
            if quote.contract.instrument.expiry == expiry
        )

        if not expiry_quotes:
            raise ValueError(
                "No historical option contracts match the requested expiry."
            )

        strike = self._resolve_strike(
            selector,
            expiry_quotes,
            chain.underlying_price,
        )

        matches = tuple(
            quote
            for quote in expiry_quotes
            if quote.contract.instrument.strike == strike
        )

        if not matches:
            raise ValueError(
                "No historical option contract matches the requested strike."
            )

        if len(matches) > 1:
            raise ValueError(
                "Historical option chain contains duplicate contracts."
            )

        instrument = matches[0].contract.instrument

        return HistoricalOptionContract(
            instrument=Instrument(
                symbol=instrument.symbol,
                exchange=instrument.exchange,
                instrument_type=InstrumentType.OPTION,
                expiry=instrument.expiry,
                strike=instrument.strike,
                option_type=instrument.option_type,
            ),
            resolved_at=as_of,
        )

    @staticmethod
    def _validate_as_of(
        chain: HistoricalOptionChainSnapshot,
        as_of: datetime,
    ) -> None:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware.")

        if chain.timestamp > as_of:
            raise ValueError("chain snapshot is after as_of.")

    @staticmethod
    def _resolve_expiry(
        selector: OptionSelector,
        quotes: tuple,
        as_of: datetime,
    ) -> str:
        available = sorted(
            {
                quote.contract.instrument.expiry
                for quote in quotes
                if quote.contract.instrument.expiry is not None
            }
        )

        if not available:
            raise ValueError(
                "Historical option chain contains no expiries."
            )

        if selector.expiry_selection is ExpirySelection.EXACT:
            if selector.expiry not in available:
                raise ValueError(
                    "Requested exact expiry is not available in the "
                    "historical option chain."
                )
            return selector.expiry

        if selector.expiry_selection is ExpirySelection.CURRENT_WEEK:
            return HistoricalOptionContractResolver._select_week_expiry(
                available,
                as_of,
                offset=0,
            )

        if selector.expiry_selection is ExpirySelection.NEXT_WEEK:
            return HistoricalOptionContractResolver._select_week_expiry(
                available,
                as_of,
                offset=1,
            )

        if selector.expiry_selection is ExpirySelection.CURRENT_MONTH:
            return HistoricalOptionContractResolver._select_month_expiry(
                available,
                as_of,
                offset=0,
            )

        if selector.expiry_selection is ExpirySelection.NEXT_MONTH:
            return HistoricalOptionContractResolver._select_month_expiry(
                available,
                as_of,
                offset=1,
            )

        raise ValueError(
            f"Unsupported expiry selection: {selector.expiry_selection.value}"
        )

    @staticmethod
    def _select_week_expiry(
        expiries: list[str],
        as_of: datetime,
        *,
        offset: int,
    ) -> str:
        future = [
            expiry
            for expiry in expiries
            if datetime.fromisoformat(expiry).date() >= as_of.date()
        ]

        if len(future) <= offset:
            raise ValueError(
                "Requested weekly expiry is not available."
            )

        return future[offset]

    @staticmethod
    def _select_month_expiry(
        expiries: list[str],
        as_of: datetime,
        *,
        offset: int,
    ) -> str:
        month_keys = sorted(
            {
                (int(expiry[:4]), int(expiry[5:7]))
                for expiry in expiries
                if expiry >= as_of.strftime("%Y-%m-%d")
            }
        )

        if len(month_keys) <= offset:
            raise ValueError(
                "Requested monthly expiry is not available."
            )

        year, month = month_keys[offset]

        month_expiries = [
            expiry
            for expiry in expiries
            if int(expiry[:4]) == year
            and int(expiry[5:7]) == month
            and expiry >= as_of.strftime("%Y-%m-%d")
        ]

        return min(month_expiries)

    @staticmethod
    def _resolve_strike(
        selector: OptionSelector,
        quotes: tuple,
        underlying_price: float,
    ) -> float:
        strikes = sorted(
            {
                quote.contract.instrument.strike
                for quote in quotes
                if quote.contract.instrument.strike is not None
            }
        )

        if not strikes:
            raise ValueError(
                "Historical option chain contains no strikes."
            )

        if selector.strike_selection is StrikeSelection.EXACT:
            assert selector.strike is not None

            if selector.strike not in strikes:
                raise ValueError(
                    "Requested exact strike is not available in the "
                    "historical option chain."
                )

            return selector.strike

        if selector.strike_selection is StrikeSelection.ATM:
            return min(
                strikes,
                key=lambda strike: (
                    abs(strike - underlying_price),
                    strike,
                ),
            )

        if selector.option_type is OptionType.CALL:
            if selector.strike_selection is StrikeSelection.ITM:
                candidates = [
                    strike
                    for strike in strikes
                    if strike <= underlying_price
                ]
                if not candidates:
                    raise ValueError(
                        "No ITM call strike is available."
                    )
                return max(candidates)

            if selector.strike_selection is StrikeSelection.OTM:
                candidates = [
                    strike
                    for strike in strikes
                    if strike > underlying_price
                ]
                if not candidates:
                    raise ValueError(
                        "No OTM call strike is available."
                    )
                return min(candidates)

        if selector.option_type is OptionType.PUT:
            if selector.strike_selection is StrikeSelection.ITM:
                candidates = [
                    strike
                    for strike in strikes
                    if strike >= underlying_price
                ]
                if not candidates:
                    raise ValueError(
                        "No ITM put strike is available."
                    )
                return min(candidates)

            if selector.strike_selection is StrikeSelection.OTM:
                candidates = [
                    strike
                    for strike in strikes
                    if strike < underlying_price
                ]
                if not candidates:
                    raise ValueError(
                        "No OTM put strike is available."
                    )
                return max(candidates)

        raise ValueError(
            f"Unsupported strike selection: {selector.strike_selection.value}"
        )
