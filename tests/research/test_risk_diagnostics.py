from datetime import UTC, datetime

from private_quant_terminal.data.economics import (
    HistoricalInstrumentEconomics,
    InMemoryHistoricalInstrumentEconomicsProvider,
    MarginRequirementType,
)
from private_quant_terminal.models.instrument import Instrument, InstrumentType
from private_quant_terminal.research.risk_diagnostics import (
    ResearchRiskDiagnosticsCalculator,
)
from private_quant_terminal.research.simulation import (
    ResearchLegPosition,
    ResearchSimulationStep,
)


def _instrument(symbol: str) -> Instrument:
    return Instrument(
        symbol=symbol,
        exchange="NSE",
        instrument_type=InstrumentType.EQUITY,
    )


def _step(
    timestamp: datetime,
    equity: float,
    positions: tuple[ResearchLegPosition, ...] = (),
) -> ResearchSimulationStep:
    return ResearchSimulationStep(
        timestamp=timestamp,
        positions=positions,
        position_marks=tuple(
            (position.instrument.identifier, position.average_price) for position in positions
        ),
        equity=equity,
    )


def test_empty_steps_return_zero_risk() -> None:
    result = ResearchRiskDiagnosticsCalculator().calculate(())

    assert result.observation_count == 0
    assert result.maximum_gross_exposure == 0.0
    assert result.maximum_position_concentration == 0.0


def test_calculates_exposure_and_concentration() -> None:
    positions = (
        ResearchLegPosition(
            group_id="G1",
            instrument=_instrument("AAA"),
            quantity=100,
            average_price=100,
        ),
        ResearchLegPosition(
            group_id="G2",
            instrument=_instrument("BBB"),
            quantity=-50,
            average_price=100,
        ),
    )

    result = ResearchRiskDiagnosticsCalculator().calculate(
        (
            _step(
                datetime(2026, 1, 1, 10, tzinfo=UTC),
                20000,
                positions,
            ),
        )
    )

    assert result.maximum_gross_exposure == 15000
    assert result.maximum_long_exposure == 10000
    assert result.maximum_short_exposure == 5000
    assert result.maximum_net_exposure == 5000
    assert result.maximum_position_concentration == 10000 / 15000
    assert result.maximum_gross_exposure_ratio == 15000 / 20000


def test_exposure_uses_historical_position_mark() -> None:
    position = ResearchLegPosition(
        group_id="G1",
        instrument=_instrument("AAA"),
        quantity=100,
        average_price=100,
    )

    result = ResearchRiskDiagnosticsCalculator().calculate(
        (
            ResearchSimulationStep(
                timestamp=datetime(2026, 1, 1, 10, tzinfo=UTC),
                positions=(position,),
                position_marks=((position.instrument.identifier, 125.0),),
                equity=20000,
            ),
        )
    )

    assert result.maximum_gross_exposure == 12500
    assert result.maximum_gross_exposure != 10000


def test_missing_historical_position_mark_is_rejected() -> None:
    position = ResearchLegPosition(
        group_id="G1",
        instrument=_instrument("AAA"),
        quantity=100,
        average_price=100,
    )

    try:
        ResearchRiskDiagnosticsCalculator().calculate(
            (
                ResearchSimulationStep(
                    timestamp=datetime(2026, 1, 1, 10, tzinfo=UTC),
                    positions=(position,),
                    equity=20000,
                ),
            )
        )
    except ValueError as exc:
        assert "Missing historical marks" in str(exc)
    else:
        raise AssertionError("Expected missing historical mark to be rejected.")


def test_calculates_observation_and_daily_losses() -> None:
    result = ResearchRiskDiagnosticsCalculator().calculate(
        (
            _step(datetime(2026, 1, 1, 10, tzinfo=UTC), 10000),
            _step(datetime(2026, 1, 1, 11, tzinfo=UTC), 9700),
            _step(datetime(2026, 1, 2, 10, tzinfo=UTC), 9000),
        )
    )

    assert result.worst_observation_loss == -700
    assert result.worst_daily_loss == -700


def test_calculates_notional_using_historical_contract_multiplier() -> None:
    position = ResearchLegPosition(
        group_id="G1",
        instrument=_instrument("NIFTY-FUT"),
        quantity=2,
        average_price=100,
    )
    timestamp = datetime(2026, 1, 1, 10, tzinfo=UTC)

    economics = HistoricalInstrumentEconomics(
        instrument=position.instrument,
        timestamp=timestamp,
        contract_multiplier=50,
    )
    provider = InMemoryHistoricalInstrumentEconomicsProvider((economics,))

    result = ResearchRiskDiagnosticsCalculator(
        economics_provider=provider,
    ).calculate(
        (
            ResearchSimulationStep(
                timestamp=timestamp,
                positions=(position,),
                position_marks=((position.instrument.identifier, 125.0),),
                equity=20000,
            ),
        )
    )

    assert result.maximum_gross_exposure == 12500
    assert result.maximum_net_exposure == 12500
    assert result.maximum_gross_leverage == 0.625
    assert result.maximum_net_leverage == 0.625


def test_calculates_historical_margin_and_margin_utilization() -> None:
    position = ResearchLegPosition(
        group_id="G1",
        instrument=_instrument("NIFTY-FUT"),
        quantity=2,
        average_price=100,
    )
    timestamp = datetime(2026, 1, 1, 10, tzinfo=UTC)

    economics = HistoricalInstrumentEconomics(
        instrument=position.instrument,
        timestamp=timestamp,
        contract_multiplier=50,
        margin_requirement=4000,
        margin_requirement_type=MarginRequirementType.ABSOLUTE,
    )
    provider = InMemoryHistoricalInstrumentEconomicsProvider((economics,))

    result = ResearchRiskDiagnosticsCalculator(
        economics_provider=provider,
    ).calculate(
        (
            ResearchSimulationStep(
                timestamp=timestamp,
                positions=(position,),
                position_marks=((position.instrument.identifier, 125.0),),
                equity=20000,
            ),
        )
    )

    assert result.maximum_required_margin == 8000
    assert result.maximum_margin_utilization == 0.4
    assert result.margin_data_available is True


def test_margin_is_explicitly_unavailable_without_historical_margin_data() -> None:
    position = ResearchLegPosition(
        group_id="G1",
        instrument=_instrument("AAA"),
        quantity=100,
        average_price=100,
    )
    timestamp = datetime(2026, 1, 1, 10, tzinfo=UTC)

    economics = HistoricalInstrumentEconomics(
        instrument=position.instrument,
        timestamp=timestamp,
        contract_multiplier=1,
    )
    provider = InMemoryHistoricalInstrumentEconomicsProvider((economics,))

    result = ResearchRiskDiagnosticsCalculator(
        economics_provider=provider,
    ).calculate(
        (
            ResearchSimulationStep(
                timestamp=timestamp,
                positions=(position,),
                position_marks=((position.instrument.identifier, 125.0),),
                equity=20000,
            ),
        )
    )

    assert result.maximum_gross_exposure == 12500
    assert result.maximum_gross_leverage == 0.625
    assert result.maximum_required_margin == 0.0
    assert result.maximum_margin_utilization == 0.0
    assert result.margin_data_available is False


def test_historical_economics_are_resolved_point_in_time() -> None:
    position = ResearchLegPosition(
        group_id="G1",
        instrument=_instrument("NIFTY-FUT"),
        quantity=1,
        average_price=100,
    )
    first = datetime(2026, 1, 1, 10, tzinfo=UTC)
    second = datetime(2026, 1, 1, 11, tzinfo=UTC)

    provider = InMemoryHistoricalInstrumentEconomicsProvider(
        (
            HistoricalInstrumentEconomics(
                instrument=position.instrument,
                timestamp=first,
                contract_multiplier=50,
            ),
            HistoricalInstrumentEconomics(
                instrument=position.instrument,
                timestamp=second,
                contract_multiplier=75,
            ),
        )
    )

    result = ResearchRiskDiagnosticsCalculator(
        economics_provider=provider,
    ).calculate(
        (
            ResearchSimulationStep(
                timestamp=first,
                positions=(position,),
                position_marks=((position.instrument.identifier, 100.0),),
                equity=10000,
            ),
            ResearchSimulationStep(
                timestamp=second,
                positions=(position,),
                position_marks=((position.instrument.identifier, 100.0),),
                equity=10000,
            ),
        )
    )

    assert result.maximum_gross_exposure == 7500
    assert result.maximum_gross_leverage == 0.75
