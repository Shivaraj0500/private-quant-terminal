class BrokerError(Exception):
    """Base exception for broker-related errors."""


class BrokerConnectionError(BrokerError):
    """Raised when a connection to a broker cannot be established."""


class BrokerAuthenticationError(BrokerError):
    """Raised when broker authentication fails."""


class BrokerOrderError(BrokerError):
    """Raised when a broker order operation fails."""


class BrokerNotFoundError(BrokerError):
    """Raised when a requested broker cannot be found."""