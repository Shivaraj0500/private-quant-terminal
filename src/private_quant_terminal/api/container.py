from private_quant_terminal.brokers.in_memory_execution import (
    InMemoryBrokerExecution,
)
from private_quant_terminal.brokers.upstox.session import (
    UpstoxSessionStore,
)
from private_quant_terminal.core.config import settings
from private_quant_terminal.data.providers.development import (
    DevelopmentMarketDataProvider,
)
from private_quant_terminal.data.repository import CandleRepository
from private_quant_terminal.execution.engine import ExecutionEngine
from private_quant_terminal.persistence import Database
from private_quant_terminal.portfolio.drawdown import (
    DrawdownCalculator,
)
from private_quant_terminal.portfolio.performance_calculator import (
    PortfolioPerformanceCalculator,
)
from private_quant_terminal.portfolio.position_manager import PositionManager
from private_quant_terminal.portfolio.risk_calculator import (
    PortfolioRiskCalculator,
)
from private_quant_terminal.portfolio.valuation import (
    PortfolioValuationService,
)
from private_quant_terminal.research.repository import (
    ResearchRunRepository,
)
from private_quant_terminal.research.service import (
    ResearchRunService,
)
from private_quant_terminal.risk.limits import RiskLimits
from private_quant_terminal.risk.manager import RiskManager
from private_quant_terminal.services.broker_execution import (
    BrokerExecutionService,
)
from private_quant_terminal.services.market_data import MarketDataService
from private_quant_terminal.services.portfolio import PortfolioService
from private_quant_terminal.services.trading_execution import (
    TradingExecutionService,
)
from private_quant_terminal.services.trading_workflow import (
    TradingWorkflowService,
)
from private_quant_terminal.strategy.repository import (
    StrategyVersionRepository,
)


class ApplicationContainer:
    """Hold shared application services and state."""

    def __init__(self) -> None:
        self.upstox_session_store = UpstoxSessionStore()

        self.database = Database(
            settings.data_dir / "private_quant_terminal.db"
        )

        self.strategy_repository = StrategyVersionRepository(
            self.database
        )

        self.research_repository = ResearchRunRepository(
            self.database
        )

        self.research_service = ResearchRunService(
            repository=self.research_repository
        )

        self.position_manager = PositionManager()

        self.candle_repository = CandleRepository()
        self.market_data_provider = DevelopmentMarketDataProvider()
        self.market_data_service = MarketDataService(
            provider=self.market_data_provider,
            candle_repository=self.candle_repository,
        )

        self.portfolio_service = PortfolioService(
            position_manager=self.position_manager,
            valuation_service=PortfolioValuationService(
                self.position_manager
            ),
            risk_calculator=PortfolioRiskCalculator(),
            performance_calculator=PortfolioPerformanceCalculator(),
            drawdown_calculator=DrawdownCalculator(),
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
