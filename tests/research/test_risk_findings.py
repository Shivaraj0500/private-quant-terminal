from private_quant_terminal.research.risk_diagnostics import (
    ResearchRiskDiagnostics,
)
from private_quant_terminal.research.risk_findings import (
    ResearchRiskFindingsCalculator,
)


def _diagnostics() -> ResearchRiskDiagnostics:
    return ResearchRiskDiagnostics(
        observation_count=10,
        maximum_gross_exposure=15000.0,
        average_gross_exposure=8000.0,
        maximum_net_exposure=5000.0,
        maximum_long_exposure=10000.0,
        maximum_short_exposure=5000.0,
        maximum_position_concentration=2 / 3,
        maximum_gross_exposure_ratio=0.75,
        maximum_net_exposure_ratio=0.25,
        worst_observation_loss=-700.0,
        worst_daily_loss=-900.0,
    )


def test_generates_exposure_findings() -> None:
    findings = ResearchRiskFindingsCalculator().calculate(_diagnostics())

    categories = {finding.category for finding in findings}

    assert "gross_exposure" in categories
    assert "net_exposure" in categories
    assert "long_exposure" in categories
    assert "short_exposure" in categories


def test_generates_concentration_and_ratio_findings() -> None:
    findings = ResearchRiskFindingsCalculator().calculate(_diagnostics())

    categories = {finding.category for finding in findings}

    assert "position_concentration" in categories
    assert "gross_exposure_ratio" in categories
    assert "net_exposure_ratio" in categories

    concentration = next(
        finding
        for finding in findings
        if finding.category == "position_concentration"
    )

    assert "66.67%" in concentration.statement


def test_generates_loss_findings() -> None:
    findings = ResearchRiskFindingsCalculator().calculate(_diagnostics())

    categories = {finding.category for finding in findings}

    assert "observation_loss" in categories
    assert "daily_loss" in categories

    daily_loss = next(
        finding
        for finding in findings
        if finding.category == "daily_loss"
    )

    assert "-900.00" in daily_loss.statement


def test_empty_observations_produce_data_availability_finding() -> None:
    diagnostics = ResearchRiskDiagnostics(
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

    findings = ResearchRiskFindingsCalculator().calculate(diagnostics)

    assert len(findings) == 1
    assert findings[0].category == "data_availability"
    assert findings[0].evidence == "observation_count=0"
