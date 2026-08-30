from fastapi import APIRouter, Request

from private_quant_terminal.api.container import ApplicationContainer
from private_quant_terminal.api.schemas.trading import (
    TradingRequest,
    TradingResponse,
)
from private_quant_terminal.strategies.signal import Signal

router = APIRouter(
    prefix="/trading",
    tags=["trading"],
)


@router.post(
    "/execute",
    response_model=TradingResponse,
)
def execute_trading_signal(
    trading_request: TradingRequest,
    request: Request,
) -> TradingResponse:
    """Execute a trading signal through the configured workflow."""
    container: ApplicationContainer = request.app.state.container

    workflow_result = container.trading_workflow_service.execute(
        Signal(
            symbol=trading_request.symbol,
            signal_type=trading_request.signal_type,
            price=trading_request.price,
        )
    )

    trading_execution_result = workflow_result.execution_result
    execution_report = (
        trading_execution_result.execution_report
        if trading_execution_result is not None
        else None
    )

    return TradingResponse(
        completed=(
            trading_execution_result.completed
            if trading_execution_result is not None
            else False
        ),
        reason=(
            trading_execution_result.reason
            if trading_execution_result is not None
            else None
        ),
        order_id=(
            execution_report.order_id
            if execution_report is not None
            else None
        ),
        average_price=(
            execution_report.average_price
            if execution_report is not None
            else None
        ),
        filled_quantity=(
            execution_report.filled_quantity
            if execution_report is not None
            else None
        ),
    )