from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from private_quant_terminal.research.simulation import ResearchSimulationStep


@dataclass(frozen=True)
class ResearchRiskDiagnostics:
    observation_count: int
    maximum_gross_exposure: float
    average_gross_exposure: float
    maximum_net_exposure: float
    maximum_long_exposure: float
    maximum_short_exposure: float
    maximum_position_concentration: float
    maximum_gross_exposure_ratio: float
    maximum_net_exposure_ratio: float
    worst_observation_loss: float
    worst_daily_loss: float


class ResearchRiskDiagnosticsCalculator:
    """Calculate deterministic risk diagnostics from research observations."""

    def calculate(
        self,
        steps: tuple[ResearchSimulationStep, ...],
    ) -> ResearchRiskDiagnostics:
        if not steps:
            return ResearchRiskDiagnostics(
                observation_count=0,
                maximum_gross_exposure=0.0,
                average_gross_exposure=0.0,
                maximum_net_exposure=0.0,
                maximum_long_exposure=0.0,
                maximum_short_exposure=0.0,
                maximum_position_concentration=0.0,
                maximum_gross_exposure_ratio=0.0,
                maximum_net_exposure_ratio=0.0,
                worst_observation_loss=0.0,
                worst_daily_loss=0.0,
            )

        gross_exposures: list[float] = []
        net_exposures: list[float] = []
        long_exposures: list[float] = []
        short_exposures: list[float] = []
        concentrations: list[float] = []
        gross_ratios: list[float] = []
        net_ratios: list[float] = []
        observation_losses: list[float] = []

        previous_equity: float | None = None
        daily_equity: dict[date, float] = {}

        for step in steps:
            long_exposure = 0.0
            short_exposure = 0.0
            position_exposures: list[float] = []

            position_marks = dict(step.position_marks)

            position_ids = {
                position.instrument.identifier for position in step.positions
            }
            mark_ids = set(position_marks)

            missing_marks = position_ids - mark_ids
            if missing_marks:
                raise ValueError(
                    "Missing historical marks for positions: "
                    + ", ".join(sorted(missing_marks))
                )

            unexpected_marks = mark_ids - position_ids
            if unexpected_marks:
                raise ValueError(
                    "Historical marks contain instruments without positions: "
                    + ", ".join(sorted(unexpected_marks))
                )

            for position in step.positions:
                market_price = position_marks[position.instrument.identifier]

                if market_price < 0:
                    raise ValueError(
                        "Historical position mark cannot be negative."
                    )

                exposure = position.quantity * market_price
                absolute_exposure = abs(exposure)
                position_exposures.append(absolute_exposure)

                if exposure > 0:
                    long_exposure += exposure
                elif exposure < 0:
                    short_exposure += absolute_exposure

            gross_exposure = long_exposure + short_exposure
            net_exposure = long_exposure - short_exposure

            concentration = (
                max(position_exposures) / gross_exposure
                if gross_exposure > 0
                else 0.0
            )

            gross_ratio = (
                gross_exposure / step.equity
                if step.equity > 0
                else 0.0
            )
            net_ratio = (
                abs(net_exposure) / step.equity
                if step.equity > 0
                else 0.0
            )

            if previous_equity is not None:
                observation_losses.append(
                    min(0.0, step.equity - previous_equity)
                )

            current_day = step.timestamp.date()
            daily_equity[current_day] = step.equity

            gross_exposures.append(gross_exposure)
            net_exposures.append(net_exposure)
            long_exposures.append(long_exposure)
            short_exposures.append(short_exposure)
            concentrations.append(concentration)
            gross_ratios.append(gross_ratio)
            net_ratios.append(net_ratio)

            previous_equity = step.equity

        daily_losses: list[float] = []
        previous_day: date | None = None
        previous_day_equity: float | None = None

        for current_day, equity in sorted(daily_equity.items()):
            if previous_day is not None and previous_day_equity is not None:
                daily_losses.append(min(0.0, equity - previous_day_equity))

            previous_day = current_day
            previous_day_equity = equity

        return ResearchRiskDiagnostics(
            observation_count=len(steps),
            maximum_gross_exposure=max(gross_exposures),
            average_gross_exposure=sum(gross_exposures) / len(gross_exposures),
            maximum_net_exposure=max(abs(value) for value in net_exposures),
            maximum_long_exposure=max(long_exposures),
            maximum_short_exposure=max(short_exposures),
            maximum_position_concentration=max(concentrations),
            maximum_gross_exposure_ratio=max(gross_ratios),
            maximum_net_exposure_ratio=max(net_ratios),
            worst_observation_loss=min(observation_losses, default=0.0),
            worst_daily_loss=min(daily_losses, default=0.0),
        )
