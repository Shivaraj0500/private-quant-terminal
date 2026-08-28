from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from private_quant_terminal.api.container import ApplicationContainer
from private_quant_terminal.brokers.upstox.auth import (
    build_authorization_url,
    consume_oauth_state,
    create_oauth_state,
)
from private_quant_terminal.brokers.upstox.config import UpstoxConfig
from private_quant_terminal.brokers.upstox.token import (
    exchange_authorization_code,
)


router = APIRouter(
    prefix="/broker/upstox",
    tags=["broker-upstox"],
)


def get_container(request: Request) -> ApplicationContainer:
    """Return the shared application container."""

    return request.app.state.container


@router.get("/login")
def login() -> RedirectResponse:
    """Redirect the user to the Upstox authorization page."""

    config = UpstoxConfig.from_environment()
    state = create_oauth_state()

    authorization_url = build_authorization_url(
        config=config,
        state=state,
    )

    return RedirectResponse(
        url=authorization_url,
        status_code=307,
    )


@router.get("/callback")
def callback(
    request: Request,
    code: str = Query(..., min_length=1),
    state: str = Query(..., min_length=1),
) -> dict[str, str]:
    """Validate OAuth callback, exchange code, and save session."""

    if not consume_oauth_state(state):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OAuth state",
        )

    config = UpstoxConfig.from_environment()

    try:
        token = exchange_authorization_code(
            config=config,
            code=code,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to exchange Upstox authorization code",
        ) from exc

    container = get_container(request)
    session = container.upstox_session_store.save(token)

    return {
        "status": "authenticated",
        "user_id": session.user_id or "",
        "user_name": session.user_name or "",
    }


@router.get("/status")
def status(
    request: Request,
) -> dict[str, str | bool]:
    """Return the current Upstox authentication status."""

    container = get_container(request)
    session = container.upstox_session_store.get()

    if session is None:
        return {
            "authenticated": False,
            "user_id": "",
            "user_name": "",
        }

    return {
        "authenticated": True,
        "user_id": session.user_id or "",
        "user_name": session.user_name or "",
    }


@router.post("/logout")
def logout(
    request: Request,
) -> dict[str, str]:
    """Clear the current Upstox session."""

    container = get_container(request)
    container.upstox_session_store.clear()

    return {
        "status": "logged_out",
    }
