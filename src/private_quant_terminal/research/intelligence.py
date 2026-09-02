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
class ResearchEvidenceReference:
    """Immutable reference to deterministic research evidence."""

    category: str
    code: str
    description: str


@dataclass(frozen=True)
class ResearchIntelligenceReport:
    """Immutable evidence-qualified interpretation of a research result."""

    conclusion: ResearchIntelligenceConclusion
    confidence: ResearchIntelligenceConfidence
    strengths: tuple[str, ...]
    limitations: tuple[str, ...]
    next_investigations: tuple[str, ...]
    evidence: tuple[ResearchEvidenceReference, ...]


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
        evidence_references: list[ResearchEvidenceReference] = []

        if integrity.passed:
            strengths.append("Research execution passed integrity validation.")
            evidence_references.append(
                ResearchEvidenceReference(
                    category="INTEGRITY",
                    code="INTEGRITY_OK",
                    description="Research execution passed integrity validation.",
                )
            )

        if trading.total_pnl > 0:
            description = "Completed trades produced positive total P&L."
            strengths.append(description)
            evidence_references.append(
                ResearchEvidenceReference(
                    category="PERFORMANCE",
                    code="TOTAL_PNL_POSITIVE",
                    description=description,
                )
            )
        elif trading.total_pnl < 0:
            description = "Completed trades provide measurable negative P&L evidence."
            strengths.append(description)
            evidence_references.append(
                ResearchEvidenceReference(
                    category="PERFORMANCE",
                    code="TOTAL_PNL_NEGATIVE",
                    description=description,
                )
            )

        if trading.profit_factor > 1.0:
            description = "Gross profit exceeded gross loss."
            strengths.append(description)
            evidence_references.append(
                ResearchEvidenceReference(
                    category="PERFORMANCE",
                    code="PROFIT_FACTOR_ABOVE_ONE",
                    description=description,
                )
            )
        elif trading.profit_factor == 1.0:
            description = "Gross profit and gross loss were equal."
            limitations.append(description)
            evidence_references.append(
                ResearchEvidenceReference(
                    category="PERFORMANCE",
                    code="PROFIT_FACTOR_EQUAL_ONE",
                    description=description,
                )
            )

        if evidence.has_open_position:
            description = (
                "The research result contains an open position, "
                "so the evidence is not fully closed."
            )
            limitations.append(description)
            evidence_references.append(
                ResearchEvidenceReference(
                    category="EXECUTION",
                    code="OPEN_POSITION",
                    description=description,
                )
            )

        if evidence.completed_trade_count == 0:
            description = (
                "No completed trades are available for performance interpretation."
            )
            limitations.append(description)
            evidence_references.append(
                ResearchEvidenceReference(
                    category="PERFORMANCE",
                    code="NO_COMPLETED_TRADES",
                    description=description,
                )
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
            evidence_references.extend(
                ResearchEvidenceReference(
                    category="INTEGRITY",
                    code=finding.code,
                    description=finding.message,
                )
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
            evidence=tuple(evidence_references),
        )
