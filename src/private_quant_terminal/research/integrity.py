from dataclasses import dataclass
from enum import Enum
from math import isclose, isfinite

from private_quant_terminal.research.execution import (
    ResearchExecutionEventType,
    ResearchExecutionResult,
)


class ResearchIntegritySeverity(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class ResearchIntegrityStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class ResearchIntegrityFinding:
    severity: ResearchIntegritySeverity
    code: str
    message: str


@dataclass(frozen=True)
class ResearchIntegrityReport:
    status: ResearchIntegrityStatus
    findings: tuple[ResearchIntegrityFinding, ...]

    @property
    def passed(self) -> bool:
        return self.status is ResearchIntegrityStatus.PASS

    @property
    def warnings(self) -> int:
        return sum(
            finding.severity is ResearchIntegritySeverity.WARN
            for finding in self.findings
        )

    @property
    def failures(self) -> int:
        return sum(
            finding.severity is ResearchIntegritySeverity.FAIL
            for finding in self.findings
        )


class ResearchIntegrityAnalyzer:
    """Validate deterministic research execution evidence."""

    _TOLERANCE = 1e-9

    def analyze(
        self,
        execution: ResearchExecutionResult,
    ) -> ResearchIntegrityReport:
        findings: list[ResearchIntegrityFinding] = []

        self._check_run_id(execution, findings)
        self._check_events(execution, findings)
        self._check_trades(execution, findings)
        self._check_equity_curve(execution, findings)
        self._check_equity_reconciliation(execution, findings)

        if not findings:
            findings.append(
                ResearchIntegrityFinding(
                    severity=ResearchIntegritySeverity.PASS,
                    code="INTEGRITY_OK",
                    message="Research execution evidence passed all integrity checks.",
                )
            )

        return ResearchIntegrityReport(
            status=self._status(findings),
            findings=tuple(findings),
        )

    @staticmethod
    def _check_run_id(
        execution: ResearchExecutionResult,
        findings: list[ResearchIntegrityFinding],
    ) -> None:
        if not execution.run_id.strip():
            findings.append(
                ResearchIntegrityFinding(
                    severity=ResearchIntegritySeverity.FAIL,
                    code="EMPTY_RUN_ID",
                    message="Research execution run_id must not be empty.",
                )
            )

    def _check_events(
        self,
        execution: ResearchExecutionResult,
        findings: list[ResearchIntegrityFinding],
    ) -> None:
        previous_timestamp = None
        entry_count = 0
        exit_count = 0

        for index, event in enumerate(execution.events):
            if (
                previous_timestamp is not None
                and event.timestamp < previous_timestamp
            ):
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="EVENTS_NOT_CHRONOLOGICAL",
                        message=f"Execution event {index} occurs before the previous event.",
                    )
                )

            previous_timestamp = event.timestamp

            if not isfinite(event.price) or event.price <= 0.0:
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="INVALID_EVENT_PRICE",
                        message=f"Execution event {index} has an invalid price.",
                    )
                )

            if not isfinite(event.quantity) or event.quantity <= 0.0:
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="INVALID_EVENT_QUANTITY",
                        message=f"Execution event {index} has an invalid quantity.",
                    )
                )

            if event.event_type is ResearchExecutionEventType.ENTRY:
                entry_count += 1
            elif event.event_type is ResearchExecutionEventType.EXIT:
                exit_count += 1

        if entry_count > exit_count:
            findings.append(
                ResearchIntegrityFinding(
                    severity=ResearchIntegritySeverity.WARN,
                    code="OPEN_POSITION",
                    message="Execution contains an unmatched ENTRY event.",
                )
            )

        if exit_count > entry_count:
            findings.append(
                ResearchIntegrityFinding(
                    severity=ResearchIntegritySeverity.FAIL,
                    code="UNMATCHED_EXIT",
                    message="Execution contains more EXIT events than ENTRY events.",
                )
            )

    def _check_trades(
        self,
        execution: ResearchExecutionResult,
        findings: list[ResearchIntegrityFinding],
    ) -> None:
        for index, trade in enumerate(execution.trades):
            if trade.entry_time > trade.exit_time:
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="TRADE_TIME_ORDER",
                        message=f"Trade {index} exits before its entry.",
                    )
                )

            if not isfinite(trade.entry_price) or trade.entry_price <= 0.0:
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="INVALID_ENTRY_PRICE",
                        message=f"Trade {index} has an invalid entry price.",
                    )
                )

            if not isfinite(trade.exit_price) or trade.exit_price <= 0.0:
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="INVALID_EXIT_PRICE",
                        message=f"Trade {index} has an invalid exit price.",
                    )
                )

            if not isfinite(trade.quantity) or trade.quantity <= 0.0:
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="INVALID_TRADE_QUANTITY",
                        message=f"Trade {index} has an invalid quantity.",
                    )
                )

            if not isfinite(trade.gross_pnl):
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="NON_FINITE_GROSS_PNL",
                        message=f"Trade {index} has a non-finite gross P&L.",
                    )
                )

            if not isfinite(trade.transaction_cost) or trade.transaction_cost < 0.0:
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="INVALID_TRANSACTION_COST",
                        message=f"Trade {index} has an invalid transaction cost.",
                    )
                )

            if not isfinite(trade.net_pnl):
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="NON_FINITE_NET_PNL",
                        message=f"Trade {index} has a non-finite net P&L.",
                    )
                )

            expected_gross_pnl = (
                trade.exit_price - trade.entry_price
            ) * trade.quantity

            if not isclose(
                trade.gross_pnl,
                expected_gross_pnl,
                rel_tol=self._TOLERANCE,
                abs_tol=self._TOLERANCE,
            ):
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="GROSS_PNL_MISMATCH",
                        message=f"Trade {index} gross P&L does not reconcile.",
                    )
                )

            expected_net_pnl = trade.gross_pnl - trade.transaction_cost

            if not isclose(
                trade.net_pnl,
                expected_net_pnl,
                rel_tol=self._TOLERANCE,
                abs_tol=self._TOLERANCE,
            ):
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="NET_PNL_MISMATCH",
                        message=f"Trade {index} net P&L does not reconcile.",
                    )
                )

    def _check_equity_curve(
        self,
        execution: ResearchExecutionResult,
        findings: list[ResearchIntegrityFinding],
    ) -> None:
        if not execution.equity_curve:
            findings.append(
                ResearchIntegrityFinding(
                    severity=ResearchIntegritySeverity.WARN,
                    code="EMPTY_EQUITY_CURVE",
                    message="Execution contains no equity curve.",
                )
            )
            return

        previous_timestamp = None

        for index, point in enumerate(execution.equity_curve):
            if (
                previous_timestamp is not None
                and point.timestamp < previous_timestamp
            ):
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="EQUITY_NOT_CHRONOLOGICAL",
                        message=f"Equity point {index} occurs before the previous point.",
                    )
                )

            previous_timestamp = point.timestamp

            if not isfinite(point.equity):
                findings.append(
                    ResearchIntegrityFinding(
                        severity=ResearchIntegritySeverity.FAIL,
                        code="NON_FINITE_EQUITY",
                        message=f"Equity point {index} is non-finite.",
                    )
                )

        if not isfinite(execution.final_equity):
            findings.append(
                ResearchIntegrityFinding(
                    severity=ResearchIntegritySeverity.FAIL,
                    code="NON_FINITE_FINAL_EQUITY",
                    message="Final equity is non-finite.",
                )
            )

    def _check_equity_reconciliation(
        self,
        execution: ResearchExecutionResult,
        findings: list[ResearchIntegrityFinding],
    ) -> None:
        if not execution.equity_curve:
            return

        initial_equity = execution.equity_curve[0].equity
        realized_pnl = sum(trade.net_pnl for trade in execution.trades)
        expected_final_equity = initial_equity + realized_pnl

        if not isclose(
            execution.final_equity,
            expected_final_equity,
            rel_tol=self._TOLERANCE,
            abs_tol=self._TOLERANCE,
        ):
            findings.append(
                ResearchIntegrityFinding(
                    severity=ResearchIntegritySeverity.FAIL,
                    code="FINAL_EQUITY_MISMATCH",
                    message=(
                        "Final equity does not reconcile with initial equity "
                        "and realized trade P&L."
                    ),
                )
            )

    @staticmethod
    def _status(
        findings: list[ResearchIntegrityFinding],
    ) -> ResearchIntegrityStatus:
        if any(
            finding.severity is ResearchIntegritySeverity.FAIL
            for finding in findings
        ):
            return ResearchIntegrityStatus.FAIL

        if any(
            finding.severity is ResearchIntegritySeverity.WARN
            for finding in findings
        ):
            return ResearchIntegrityStatus.WARN

        return ResearchIntegrityStatus.PASS
