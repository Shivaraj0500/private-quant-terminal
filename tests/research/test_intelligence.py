from types import SimpleNamespace

from private_quant_terminal.research.intelligence import (
    ResearchIntelligenceAnalyzer,
    ResearchIntelligenceConclusion,
    ResearchIntelligenceConfidence,
)


def make_performance(
    *,
    total_pnl: float,
    profit_factor: float,
    completed_trade_count: int,
    has_open_position: bool = False,
):
    return SimpleNamespace(
        trading_performance=SimpleNamespace(
            total_pnl=total_pnl,
            profit_factor=profit_factor,
        ),
        evidence_summary=SimpleNamespace(
            completed_trade_count=completed_trade_count,
            has_open_position=has_open_position,
        ),
    )


def make_integrity(warnings=()):
    from private_quant_terminal.research.integrity import (
        ResearchIntegrityFinding,
        ResearchIntegritySeverity,
        ResearchIntegrityStatus,
    )

    findings = tuple(
        warning
        if isinstance(warning, ResearchIntegrityFinding)
        else ResearchIntegrityFinding(
            severity=ResearchIntegritySeverity.WARN,
            code="TEST_WARNING",
            message=warning.message,
        )
        for warning in warnings
    )

    return SimpleNamespace(
        passed=True,
        warnings=len(findings),
        findings=findings,
        status=(
            ResearchIntegrityStatus.WARN
            if findings
            else ResearchIntegrityStatus.PASS
        ),
    )


def test_insufficient_evidence_without_completed_trades() -> None:
    report = ResearchIntelligenceAnalyzer().analyze(
        performance=make_performance(
            total_pnl=0.0,
            profit_factor=0.0,
            completed_trade_count=0,
        ),
        integrity=make_integrity(),
    )

    assert report.conclusion is (
        ResearchIntelligenceConclusion.INSUFFICIENT_EVIDENCE
    )
    assert report.confidence is ResearchIntelligenceConfidence.LOW
    assert report.limitations


def test_positive_evidence() -> None:
    report = ResearchIntelligenceAnalyzer().analyze(
        performance=make_performance(
            total_pnl=100.0,
            profit_factor=2.0,
            completed_trade_count=10,
        ),
        integrity=make_integrity(),
    )

    assert report.conclusion is ResearchIntelligenceConclusion.POSITIVE_EVIDENCE
    assert report.confidence is ResearchIntelligenceConfidence.HIGH
    assert report.strengths


def test_negative_evidence() -> None:
    report = ResearchIntelligenceAnalyzer().analyze(
        performance=make_performance(
            total_pnl=-100.0,
            profit_factor=0.5,
            completed_trade_count=10,
        ),
        integrity=make_integrity(),
    )

    assert report.conclusion is ResearchIntelligenceConclusion.NEGATIVE_EVIDENCE
    assert report.confidence is ResearchIntelligenceConfidence.HIGH
    assert report.strengths


def test_mixed_evidence() -> None:
    report = ResearchIntelligenceAnalyzer().analyze(
        performance=make_performance(
            total_pnl=100.0,
            profit_factor=0.8,
            completed_trade_count=10,
        ),
        integrity=make_integrity(),
    )

    assert report.conclusion is ResearchIntelligenceConclusion.MIXED_EVIDENCE
    assert report.confidence is ResearchIntelligenceConfidence.HIGH


def test_open_position_reduces_confidence() -> None:
    report = ResearchIntelligenceAnalyzer().analyze(
        performance=make_performance(
            total_pnl=100.0,
            profit_factor=2.0,
            completed_trade_count=10,
            has_open_position=True,
        ),
        integrity=make_integrity(),
    )

    assert report.conclusion is ResearchIntelligenceConclusion.POSITIVE_EVIDENCE
    assert report.confidence is ResearchIntelligenceConfidence.LOW
    assert any(
        "open position" in limitation
        for limitation in report.limitations
    )


def test_integrity_warning_produces_medium_confidence() -> None:
    warning = SimpleNamespace(
        message="Execution contains an integrity warning."
    )

    report = ResearchIntelligenceAnalyzer().analyze(
        performance=make_performance(
            total_pnl=100.0,
            profit_factor=2.0,
            completed_trade_count=10,
        ),
        integrity=make_integrity(warnings=(warning,)),
    )

    assert report.conclusion is ResearchIntelligenceConclusion.POSITIVE_EVIDENCE
    assert report.confidence is ResearchIntelligenceConfidence.MEDIUM
    assert "Execution contains an integrity warning." in report.limitations
