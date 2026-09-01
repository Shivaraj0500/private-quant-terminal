from dataclasses import dataclass
from enum import Enum

from private_quant_terminal.research.integrity import ResearchIntegrityReport
from private_quant_terminal.research.performance import ResearchPerformanceReport


class ResearchIntelligenceConclusion(str, Enum):
    """Evidence-qualified conclusion for a research result."""

    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    POSITIVE_EVIDENCE = "POSITIVE_EVIDENCE"
    NEGATIVE_EVIDENCE = "NEGATIVE_EVIDENCE"
    MIXED_EVIDENCE = "MIXED_EVIDENCE"


class ResearchIntelligenceConfidence(str, Enum):
    """Confidence in the completeness of the available evidence."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class ResearchIntelligenceReport:
    """Immutable evidence-qualified interpretation of a research result."""

    conclusion: ResearchIntelligenceConclusion
    confidence: ResearchIntelligenceConfidence
    strengths: tuple[str, ...]
    limitations: tuple[str, ...]
    next_investigations: tuple[str, ...]


class ResearchIntelligenceAnalyzer:
    """Interpret research evidence without generating unsupported claims."""

    def analyze(
        self,
        *,
        performance: ResearchPerformanceReport,
        integrity: ResearchIntegrityReport,
    ) -> ResearchIntelligenceReport:
        """Produce a deterministic evidence-qualified interpretation."""

        evidence = performance.evidence_summary
        trading = performance.trading_performance

        strengths: list[str] = []
        limitations: list[str] = []
        next_investigations: list[str] = []

        if integrity.passed:
            strengths.append("Research execution passed integrity validation.")

        if trading.total_pnl > 0:
            strengths.append("Completed trades produced positive total P&L.")
        elif trading.total_pnl < 0:
            strengths.append("Completed trades provide measurable negative P&L evidence.")

        if trading.profit_factor > 1.0:
            strengths.append("Gross profit exceeded gross loss.")
        elif trading.profit_factor == 1.0:
            limitations.append("Gross profit and gross loss were equal.")

        if evidence.has_open_position:
            limitations.append(
                "The research result contains an open position, "
                "so the evidence is not fully closed."
            )

        if evidence.completed_trade_count == 0:
            limitations.append(
                "No completed trades are available for performance interpretation."
            )

        warning_findings = tuple(
            finding
            for finding in integrity.findings
            if finding.severity.value == "WARN"
        )

        if warning_findings:
            limitations.extend(
                finding.message
                for finding in warning_findings
            )

        if evidence.completed_trade_count == 0:
            conclusion = ResearchIntelligenceConclusion.INSUFFICIENT_EVIDENCE
        elif trading.total_pnl > 0 and trading.profit_factor > 1.0:
            conclusion = ResearchIntelligenceConclusion.POSITIVE_EVIDENCE
        elif trading.total_pnl < 0 and trading.profit_factor < 1.0:
            conclusion = ResearchIntelligenceConclusion.NEGATIVE_EVIDENCE
        else:
            conclusion = ResearchIntelligenceConclusion.MIXED_EVIDENCE

        if (
            evidence.completed_trade_count == 0
            or evidence.has_open_position
            or integrity.status.value == "FAIL"
        ):
            confidence = ResearchIntelligenceConfidence.LOW
        elif integrity.status.value == "WARN":
            confidence = ResearchIntelligenceConfidence.MEDIUM
        else:
            confidence = ResearchIntelligenceConfidence.HIGH

        next_investigations.extend(
            (
                "Test robustness across alternative market periods.",
                "Evaluate sensitivity to strategy parameters.",
                "Validate the strategy on out-of-sample data.",
            )
        )

        return ResearchIntelligenceReport(
            conclusion=conclusion,
            confidence=confidence,
            strengths=tuple(strengths),
            limitations=tuple(limitations),
            next_investigations=tuple(next_investigations),
        )
