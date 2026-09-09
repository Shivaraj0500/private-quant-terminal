from datetime import datetime, timezone

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
            (position.instrument.identifier, position.average_price)
            for position in positions
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
                datetime(2026, 1, 1, 10, tzinfo=timezone.utc),
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
                timestamp=datetime(2026, 1, 1, 10, tzinfo=timezone.utc),
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
                    timestamp=datetime(2026, 1, 1, 10, tzinfo=timezone.utc),
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
            _step(datetime(2026, 1, 1, 10, tzinfo=timezone.utc), 10000),
            _step(datetime(2026, 1, 1, 11, tzinfo=timezone.utc), 9700),
            _step(datetime(2026, 1, 2, 10, tzinfo=timezone.utc), 9000),
        )
    )

    assert result.worst_observation_loss == -700
    assert result.worst_daily_loss == -700
