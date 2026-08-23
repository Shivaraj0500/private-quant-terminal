import pytest

from private_quant_terminal.brokers.session import BrokerSession


def test_broker_session_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerSession()


def test_incomplete_broker_session_is_abstract() -> None:
    class IncompleteSession(BrokerSession):
        @property
        def is_authenticated(self) -> bool:
            return False

        def authenticate(self) -> None:
            return None

    with pytest.raises(TypeError):
        IncompleteSession()


def test_complete_broker_session_can_be_instantiated() -> None:
    class CompleteSession(BrokerSession):
        def __init__(self) -> None:
            self._authenticated = False

        @property
        def is_authenticated(self) -> bool:
            return self._authenticated

        def authenticate(self) -> None:
            self._authenticated = True

        def logout(self) -> None:
            self._authenticated = False

    session = CompleteSession()

    assert isinstance(session, BrokerSession)
    assert session.is_authenticated is False


def test_broker_session_can_authenticate_and_logout() -> None:
    class CompleteSession(BrokerSession):
        def __init__(self) -> None:
            self._authenticated = False

        @property
        def is_authenticated(self) -> bool:
            return self._authenticated

        def authenticate(self) -> None:
            self._authenticated = True

        def logout(self) -> None:
            self._authenticated = False

    session = CompleteSession()

    session.authenticate()
    assert session.is_authenticated is True

    session.logout()
    assert session.is_authenticated is False


def test_broker_session_abstract_methods_raise_not_implemented() -> None:
    class ConcreteSession(BrokerSession):
        @property
        def is_authenticated(self) -> bool:
            return BrokerSession.is_authenticated.fget(self)  # type: ignore[union-attr]

        def authenticate(self) -> None:
            BrokerSession.authenticate(self)

        def logout(self) -> None:
            BrokerSession.logout(self)

    session = ConcreteSession()

    with pytest.raises(NotImplementedError):
        _ = session.is_authenticated

    with pytest.raises(NotImplementedError):
        session.authenticate()

    with pytest.raises(NotImplementedError):
        session.logout()