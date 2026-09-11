from __future__ import annotations

from dataclasses import dataclass

from private_quant_terminal.research.risk_diagnostics import (
    ResearchRiskDiagnostics,
)


@dataclass(frozen=True)
class ResearchRiskFinding:
    category: str
    statement: str
    evidence: str


class ResearchRiskFindingsCalculator:
    """Generate deterministic research findings from risk diagnostics."""

    def calculate(
        self,
        diagnostics: ResearchRiskDiagnostics,
    ) -> tuple[ResearchRiskFinding, ...]:
        findings: list[ResearchRiskFinding] = []

        if diagnostics.observation_count == 0:
            return (
                ResearchRiskFinding(
                    category="data_availability",
                    statement=("No simulation observations were available for risk analysis."),
                    evidence="observation_count=0",
                ),
            )

        findings.append(
            ResearchRiskFinding(
                category="gross_exposure",
                statement=(
                    "The strategy reached a maximum gross exposure of "
                    f"{diagnostics.maximum_gross_exposure:.2f}."
                ),
                evidence=(f"maximum_gross_exposure={diagnostics.maximum_gross_exposure:.2f}"),
            )
        )

        findings.append(
            ResearchRiskFinding(
                category="net_exposure",
                statement=(
                    "The strategy reached a maximum absolute net exposure of "
                    f"{diagnostics.maximum_net_exposure:.2f}."
                ),
                evidence=(f"maximum_net_exposure={diagnostics.maximum_net_exposure:.2f}"),
            )
        )

        if diagnostics.maximum_long_exposure > 0:
            findings.append(
                ResearchRiskFinding(
                    category="long_exposure",
                    statement=(
                        "The strategy carried long exposure, reaching a maximum "
                        f"of {diagnostics.maximum_long_exposure:.2f}."
                    ),
                    evidence=(f"maximum_long_exposure={diagnostics.maximum_long_exposure:.2f}"),
                )
            )

        if diagnostics.maximum_short_exposure > 0:
            findings.append(
                ResearchRiskFinding(
                    category="short_exposure",
                    statement=(
                        "The strategy carried short exposure, reaching a maximum "
                        f"of {diagnostics.maximum_short_exposure:.2f}."
                    ),
                    evidence=(f"maximum_short_exposure={diagnostics.maximum_short_exposure:.2f}"),
                )
            )

        if diagnostics.maximum_position_concentration > 0:
            findings.append(
                ResearchRiskFinding(
                    category="position_concentration",
                    statement=(
                        "The largest observed position represented "
                        f"{diagnostics.maximum_position_concentration:.2%} "
                        "of gross exposure."
                    ),
                    evidence=(
                        "maximum_position_concentration="
                        f"{diagnostics.maximum_position_concentration:.6f}"
                    ),
                )
            )

        findings.append(
            ResearchRiskFinding(
                category="gross_exposure_ratio",
                statement=(
                    "Maximum gross exposure reached "
                    f"{diagnostics.maximum_gross_exposure_ratio:.2%} "
                    "of observed equity."
                ),
                evidence=(
                    f"maximum_gross_exposure_ratio={diagnostics.maximum_gross_exposure_ratio:.6f}"
                ),
            )
        )

        findings.append(
            ResearchRiskFinding(
                category="net_exposure_ratio",
                statement=(
                    "Maximum absolute net exposure reached "
                    f"{diagnostics.maximum_net_exposure_ratio:.2%} "
                    "of observed equity."
                ),
                evidence=(
                    f"maximum_net_exposure_ratio={diagnostics.maximum_net_exposure_ratio:.6f}"
                ),
            )
        )

        if diagnostics.leverage_data_available:
            findings.append(
                ResearchRiskFinding(
                    category="gross_leverage",
                    statement=(
                        f"Maximum gross leverage reached {diagnostics.maximum_gross_leverage:.2%}."
                    ),
                    evidence=(f"maximum_gross_leverage={diagnostics.maximum_gross_leverage:.6f}"),
                )
            )

            findings.append(
                ResearchRiskFinding(
                    category="net_leverage",
                    statement=(
                        f"Maximum absolute net leverage reached "
                        f"{diagnostics.maximum_net_leverage:.2%}."
                    ),
                    evidence=(f"maximum_net_leverage={diagnostics.maximum_net_leverage:.6f}"),
                )
            )

            findings.append(
                ResearchRiskFinding(
                    category="leverage_data_availability",
                    statement=(
                        "Historical contract economics were available for "
                        "leverage analysis across all required observations."
                    ),
                    evidence="leverage_data_available=true",
                )
            )
        else:
            findings.append(
                ResearchRiskFinding(
                    category="leverage_data_availability",
                    statement=(
                        "Historical contract economics were unavailable for "
                        "leverage analysis, so leverage could not be established."
                    ),
                    evidence="leverage_data_available=false",
                )
            )

        if diagnostics.margin_data_available:
            findings.append(
                ResearchRiskFinding(
                    category="required_margin",
                    statement=(
                        "Maximum historical required margin reached "
                        f"{diagnostics.maximum_required_margin:.2f}."
                    ),
                    evidence=(f"maximum_required_margin={diagnostics.maximum_required_margin:.2f}"),
                )
            )

            findings.append(
                ResearchRiskFinding(
                    category="margin_utilization",
                    statement=(
                        "Maximum historical margin utilization reached "
                        f"{diagnostics.maximum_margin_utilization:.2%}."
                    ),
                    evidence=(
                        f"maximum_margin_utilization={diagnostics.maximum_margin_utilization:.6f}"
                    ),
                )
            )

            findings.append(
                ResearchRiskFinding(
                    category="margin_data_availability",
                    statement=(
                        "Historical margin requirement data was available "
                        "for all observed positions."
                    ),
                    evidence="margin_data_available=true",
                )
            )
        else:
            findings.append(
                ResearchRiskFinding(
                    category="margin_data_availability",
                    statement=(
                        "Historical margin requirement data was unavailable "
                        "for all required observations, so margin utilization "
                        "could not be established."
                    ),
                    evidence="margin_data_available=false",
                )
            )

        if diagnostics.worst_observation_loss < 0:
            findings.append(
                ResearchRiskFinding(
                    category="observation_loss",
                    statement=(
                        "The worst observed equity change between consecutive "
                        "simulation observations was "
                        f"{diagnostics.worst_observation_loss:.2f}."
                    ),
                    evidence=(f"worst_observation_loss={diagnostics.worst_observation_loss:.2f}"),
                )
            )

        if diagnostics.worst_daily_loss < 0:
            findings.append(
                ResearchRiskFinding(
                    category="daily_loss",
                    statement=(
                        "The worst observed day-to-day equity loss was "
                        f"{diagnostics.worst_daily_loss:.2f}."
                    ),
                    evidence=(f"worst_daily_loss={diagnostics.worst_daily_loss:.2f}"),
                )
            )

        return tuple(findings)
