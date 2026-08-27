from private_quant_terminal.brokers.in_memory_execution import (
    InMemoryBrokerExecution,
)
from private_quant_terminal.execution.engine import ExecutionEngine
from private_quant_terminal.portfolio.position_manager import PositionManager
from private_quant_terminal.portfolio.risk_calculator import (
    PortfolioRiskCalculator,
)
from private_quant_terminal.portfolio.valuation import (
    PortfolioValuationService,
)
from private_quant_terminal.risk.limits import RiskLimits
from private_quant_terminal.risk.manager import RiskManager
from private_quant_terminal.services.broker_execution import (
    BrokerExecutionService,
)
from private_quant_terminal.services.portfolio import PortfolioService
from private_quant_terminal.services.trading_execution import (
    TradingExecutionService,
)
from private_quant_terminal.services.trading_workflow import (
    TradingWorkflowService,
)


class ApplicationContainer:
    """Hold shared application services and state."""

    def __init__(self) -> None:
        self.position_manager = PositionManager()

        self.portfolio_service = PortfolioService(
            position_manager=self.position_manager,
            valuation_service=PortfolioValuationService(
                self.position_manager
            ),
            risk_calculator=PortfolioRiskCalculator(),
        )

        self.trading_execution_service = TradingExecutionService(
            execution_engine=ExecutionEngine(quantity=1),
            risk_manager=RiskManager(
                limits=RiskLimits(
                    max_position_quantity=1000,
                    max_order_quantity=100,
                    max_open_positions=20,
                    max_daily_loss=100000.0,
                ),
                position_manager=self.position_manager,
            ),
            broker_execution_service=BrokerExecutionService(
                InMemoryBrokerExecution()
            ),
        )

        self.trading_workflow_service = TradingWorkflowService(
            trading_execution_service=self.trading_execution_service,
            position_manager=self.position_manager,
        )