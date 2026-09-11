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
        finding for finding in findings if finding.category == "position_concentration"
    )

    assert "66.67%" in concentration.statement


def test_generates_loss_findings() -> None:
    findings = ResearchRiskFindingsCalculator().calculate(_diagnostics())

    categories = {finding.category for finding in findings}

    assert "observation_loss" in categories
    assert "daily_loss" in categories

    daily_loss = next(finding for finding in findings if finding.category == "daily_loss")

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


def test_generates_leverage_findings() -> None:
    values = _diagnostics().__dict__.copy()
    values.update(
        maximum_gross_leverage=1.50,
        maximum_net_leverage=0.75,
        leverage_data_available=True,
    )
    diagnostics = ResearchRiskDiagnostics(**values)

    findings = ResearchRiskFindingsCalculator().calculate(diagnostics)

    categories = {finding.category for finding in findings}

    assert "gross_leverage" in categories
    assert "net_leverage" in categories

    gross = next(finding for finding in findings if finding.category == "gross_leverage")
    assert "150.00%" in gross.statement


def test_generates_margin_findings_when_data_is_available() -> None:
    values = _diagnostics().__dict__.copy()
    values.update(
        maximum_required_margin=8000.0,
        maximum_margin_utilization=0.40,
        margin_data_available=True,
    )
    diagnostics = ResearchRiskDiagnostics(**values)

    findings = ResearchRiskFindingsCalculator().calculate(diagnostics)

    categories = {finding.category for finding in findings}

    assert "required_margin" in categories
    assert "margin_utilization" in categories
    assert "margin_data_availability" in categories

    margin = next(finding for finding in findings if finding.category == "required_margin")
    assert "8000.00" in margin.statement

    utilization = next(finding for finding in findings if finding.category == "margin_utilization")
    assert "40.00%" in utilization.statement


def test_generates_margin_unavailable_finding() -> None:
    values = _diagnostics().__dict__.copy()
    values["margin_data_available"] = False
    diagnostics = ResearchRiskDiagnostics(**values)

    findings = ResearchRiskFindingsCalculator().calculate(diagnostics)

    availability = next(
        finding for finding in findings if finding.category == "margin_data_availability"
    )

    assert "unavailable" in availability.statement.lower()
