from enum import Enum


class StrategyStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    RETIRED = "RETIRED"


class StrategyTimeframe(str, Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"


class ConditionOperator(str, Enum):
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="


class PositionSizingMethod(str, Enum):
    FIXED_QUANTITY = "FIXED_QUANTITY"
    FIXED_NOTIONAL = "FIXED_NOTIONAL"
    PERCENT_OF_EQUITY = "PERCENT_OF_EQUITY"
    RISK_BASED = "RISK_BASED"


class StopLossType(str, Enum):
    NONE = "NONE"
    ABSOLUTE = "ABSOLUTE"
    PERCENT = "PERCENT"
    ATR_MULTIPLE = "ATR_MULTIPLE"


class TakeProfitType(str, Enum):
    NONE = "NONE"
    ABSOLUTE = "ABSOLUTE"
    PERCENT = "PERCENT"
    RISK_REWARD = "RISK_REWARD"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
