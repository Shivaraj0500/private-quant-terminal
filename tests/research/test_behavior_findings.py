from datetime import datetime, timezone

from private_quant_terminal.research.behavior_diagnostics import (
    ResearchBehaviorDiagnostics,
)
from private_quant_terminal.research.behavior_findings import (
    ResearchBehaviorFindingsCalculator,
)


def make_diagnostics() -> ResearchBehaviorDiagnostics:
    return ResearchBehaviorDiagnostics(
        entry_hour_distribution=((9, 2), (10, 1)),
        exit_hour_distribution=((10, 2), (11, 1)),
        winning_trade_count=2,
        losing_trade_count=1,
        zero_pnl_trade_count=0,
        winning_pnl=180.0,
        losing_pnl=-70.0,
        average_winning_trade=90.0,
        average_losing_trade=-70.0,
        loss_by_entry_hour=((10, 70.0),),
    )


def test_finds_completed_trade_outcomes():
    findings = ResearchBehaviorFindingsCalculator().calculate(make_diagnostics())

    statements = tuple(finding.statement for finding in findings)

    assert "winning trades" in statements[0]
    assert any("losing trades" in statement for statement in statements)


def test_finds_payoff_asymmetry():
    findings = ResearchBehaviorFindingsCalculator().calculate(make_diagnostics())

    payoff = next(
        finding for finding in findings if finding.category == "payoff"
    )

    assert "Average winning trade magnitude exceeded" in payoff.statement
    assert "average_winning_trade=90.0" in payoff.evidence
    assert "average_losing_trade=-70.0" in payoff.evidence


def test_finds_loss_concentration():
    findings = ResearchBehaviorFindingsCalculator().calculate(make_diagnostics())

    concentration = next(
        finding
        for finding in findings
        if finding.category == "loss_concentration"
    )

    assert "10:00" in concentration.statement
    assert "absolute_loss=70.0" in concentration.evidence
    assert "share_of_entry_hour_losses=1.0" in concentration.evidence


def test_empty_sample_produces_insufficient_behavior_finding():
    diagnostics = ResearchBehaviorDiagnostics(
        entry_hour_distribution=(),
        exit_hour_distribution=(),
        winning_trade_count=0,
        losing_trade_count=0,
        zero_pnl_trade_count=0,
        winning_pnl=0.0,
        losing_pnl=0.0,
        average_winning_trade=0.0,
        average_losing_trade=0.0,
        loss_by_entry_hour=(),
    )

    findings = ResearchBehaviorFindingsCalculator().calculate(diagnostics)

    assert len(findings) == 1
    assert findings[0].category == "sample"
    assert "No completed trades" in findings[0].statement
