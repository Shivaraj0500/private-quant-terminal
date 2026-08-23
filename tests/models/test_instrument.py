import pytest

from private_quant_terminal.models.instrument import (
    Instrument,
    InstrumentType,
    OptionType,
)


class TestInstrumentEnums:
    def test_instrument_type_values(self) -> None:
        assert InstrumentType.EQUITY.value == "EQUITY"
        assert InstrumentType.INDEX.value == "INDEX"
        assert InstrumentType.FUTURE.value == "FUTURE"
        assert InstrumentType.OPTION.value == "OPTION"

    def test_option_type_values(self) -> None:
        assert OptionType.CALL.value == "CE"
        assert OptionType.PUT.value == "PE"


class TestInstrument:
    def test_creates_equity_identifier(self) -> None:
        instrument = Instrument(
            symbol="RELIANCE",
            exchange="NSE",
            instrument_type=InstrumentType.EQUITY,
        )

        assert instrument.identifier == "NSE:RELIANCE:EQUITY"

    def test_creates_index_identifier(self) -> None:
        instrument = Instrument(
            symbol="NIFTY",
            exchange="NSE",
            instrument_type=InstrumentType.INDEX,
        )

        assert instrument.identifier == "NSE:NIFTY:INDEX"

    def test_creates_future_identifier_with_expiry(self) -> None:
        instrument = Instrument(
            symbol="NIFTY",
            exchange="NFO",
            instrument_type=InstrumentType.FUTURE,
            expiry="2026-08-27",
        )

        assert instrument.identifier == "NFO:NIFTY:FUTURE:2026-08-27"

    def test_creates_option_identifier(self) -> None:
        instrument = Instrument(
            symbol="NIFTY",
            exchange="NFO",
            instrument_type=InstrumentType.OPTION,
            expiry="2026-08-27",
            strike=25000.0,
            option_type=OptionType.CALL,
        )

        assert (
            instrument.identifier
            == "NFO:NIFTY:OPTION:2026-08-27:25000.0:CE"
        )

    def test_creates_put_option_identifier(self) -> None:
        instrument = Instrument(
            symbol="BANKNIFTY",
            exchange="NFO",
            instrument_type=InstrumentType.OPTION,
            expiry="2026-08-27",
            strike=55000.0,
            option_type=OptionType.PUT,
        )

        assert (
            instrument.identifier
            == "NFO:BANKNIFTY:OPTION:2026-08-27:55000.0:PE"
        )

    def test_identifier_includes_strike_without_expiry(self) -> None:
        instrument = Instrument(
            symbol="TEST",
            exchange="NSE",
            instrument_type=InstrumentType.OPTION,
            strike=100.0,
        )

        assert instrument.identifier == "NSE:TEST:OPTION:100.0"

    def test_identifier_includes_option_type_without_other_option_fields(
        self,
    ) -> None:
        instrument = Instrument(
            symbol="TEST",
            exchange="NSE",
            instrument_type=InstrumentType.OPTION,
            option_type=OptionType.CALL,
        )

        assert instrument.identifier == "NSE:TEST:OPTION:CE"

    def test_identifier_includes_zero_strike(self) -> None:
        instrument = Instrument(
            symbol="TEST",
            exchange="NSE",
            instrument_type=InstrumentType.OPTION,
            strike=0.0,
        )

        assert instrument.identifier == "NSE:TEST:OPTION:0.0"

    def test_identifier_omits_empty_expiry(self) -> None:
        instrument = Instrument(
            symbol="TEST",
            exchange="NSE",
            instrument_type=InstrumentType.EQUITY,
            expiry="",
        )

        assert instrument.identifier == "NSE:TEST:EQUITY"

    def test_instrument_is_immutable(self) -> None:
        instrument = Instrument(
            symbol="RELIANCE",
            exchange="NSE",
            instrument_type=InstrumentType.EQUITY,
        )

        with pytest.raises(AttributeError):
            instrument.symbol = "TCS"