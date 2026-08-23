import pytest

from private_quant_terminal.brokers.account import BrokerAccount


def test_broker_account_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerAccount()


def test_incomplete_broker_account_is_abstract() -> None:
    class IncompleteAccount(BrokerAccount):
        @property
        def account_id(self) -> str:
            return "ACCOUNT-123"

        def available_cash(self) -> float:
            return 100000.0

        def used_margin(self) -> float:
            return 25000.0

    with pytest.raises(TypeError):
        IncompleteAccount()


def test_complete_broker_account_can_be_instantiated() -> None:
    class CompleteAccount(BrokerAccount):
        @property
        def account_id(self) -> str:
            return "ACCOUNT-123"

        def available_cash(self) -> float:
            return 100000.0

        def used_margin(self) -> float:
            return 25000.0

        def available_margin(self) -> float:
            return 75000.0

    account = CompleteAccount()

    assert isinstance(account, BrokerAccount)
    assert account.account_id == "ACCOUNT-123"
    assert account.available_cash() == 100000.0
    assert account.used_margin() == 25000.0
    assert account.available_margin() == 75000.0


def test_broker_account_abstract_members_raise_not_implemented() -> None:
    class ConcreteAccount(BrokerAccount):
        @property
        def account_id(self) -> str:
            return BrokerAccount.account_id.fget(self)

        def available_cash(self) -> float:
            return BrokerAccount.available_cash(self)

        def used_margin(self) -> float:
            return BrokerAccount.used_margin(self)

        def available_margin(self) -> float:
            return BrokerAccount.available_margin(self)

    account = ConcreteAccount()

    with pytest.raises(NotImplementedError):
        _ = account.account_id

    with pytest.raises(NotImplementedError):
        account.available_cash()

    with pytest.raises(NotImplementedError):
        account.used_margin()

    with pytest.raises(NotImplementedError):
        account.available_margin()