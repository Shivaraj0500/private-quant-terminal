from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from private_quant_terminal.api.container import ApplicationContainer
from private_quant_terminal.api.routes.health import (
    router as health_router,
)
from private_quant_terminal.api.routes.market_data import (
    router as market_data_router,
)
from private_quant_terminal.api.routes.portfolio import (
    router as portfolio_router,
)
from private_quant_terminal.api.routes.research import (
    router as research_router,
)
from private_quant_terminal.api.routes.strategy import (
    router as strategy_router,
)
from private_quant_terminal.api.routes.technical_analysis import (
    router as technical_analysis_router,
)
from private_quant_terminal.api.routes.trading import (
    router as trading_router,
)
from private_quant_terminal.api.routes.upstox import (
    router as upstox_router,
)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="Private Quant Terminal",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=(
            r"https://[a-z0-9-]+-[0-9]+\.app\.github\.dev"
        ),
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.container = ApplicationContainer()

    app.include_router(health_router)
    app.include_router(market_data_router)
    app.include_router(technical_analysis_router)
    app.include_router(research_router)
    app.include_router(strategy_router)
    app.include_router(portfolio_router)
    app.include_router(trading_router)
    app.include_router(upstox_router)

    return app


app = create_app()
