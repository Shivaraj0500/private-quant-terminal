from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar

import numpy as np
import talib

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.indicator_providers import (
    IndicatorProvider,
    IndicatorResult,
)
from private_quant_terminal.strategy.indicator_specs import (
    IndicatorSpec,
)
from private_quant_terminal.strategy.series import TimeSeries


class TALibIndicatorProvider(IndicatorProvider):
    """TA-Lib-backed provider for explicitly approved indicators."""

    _SUPPORTED: ClassVar[set[str]] = {
        "SMA",
        "EMA",
        "RSI",
        "ATR",
        "BBANDS",
        "MACD",
        "STOCH",
        "MOMENTUM",
        "ROC",
        "OBV",
    }

    @property
    def provider_id(self) -> str:
        return "talib"

    def supports(
        self,
        spec: IndicatorSpec,
    ) -> bool:
        return spec.id in self._SUPPORTED

    def calculate(
        self,
        spec: IndicatorSpec,
        candles: Sequence[Candle],
        parameters: dict[str, float],
    ) -> IndicatorResult:
        if not candles:
            raise ValueError("candles cannot be empty")

        if spec.id not in self._SUPPORTED:
            raise ValueError(f"TA-Lib provider does not support {spec.id}")

        timestamps = tuple(candle.timestamp for candle in candles)

        close = np.asarray(
            [candle.close for candle in candles],
            dtype=float,
        )

        high = np.asarray(
            [candle.high for candle in candles],
            dtype=float,
        )

        low = np.asarray(
            [candle.low for candle in candles],
            dtype=float,
        )

        volume = np.asarray(
            [candle.volume for candle in candles],
            dtype=float,
        )

        if spec.id == "MACD":
            fastperiod = self._period_parameter(
                parameters,
                "fastperiod",
                default=12,
            )
            slowperiod = self._period_parameter(
                parameters,
                "slowperiod",
                default=26,
            )
            signalperiod = self._period_parameter(
                parameters,
                "signalperiod",
                default=9,
            )

            if fastperiod >= slowperiod:
                raise ValueError("fastperiod must be less than slowperiod")

            macd, signal, histogram = talib.MACD(
                close,
                fastperiod=fastperiod,
                slowperiod=slowperiod,
                signalperiod=signalperiod,
            )

            return IndicatorResult(
                outputs={
                    "macd": self._series(
                        timestamps,
                        macd,
                    ),
                    "signal": self._series(
                        timestamps,
                        signal,
                    ),
                    "histogram": self._series(
                        timestamps,
                        histogram,
                    ),
                }
            )

        if spec.id == "STOCH":
            fastk_period = self._period_parameter(
                parameters,
                "fastk_period",
                default=5,
            )
            slowk_period = self._period_parameter(
                parameters,
                "slowk_period",
                default=3,
            )
            slowk_matype = self._matype_parameter(
                parameters,
                "slowk_matype",
                default=0,
            )
            slowd_period = self._period_parameter(
                parameters,
                "slowd_period",
                default=3,
            )
            slowd_matype = self._matype_parameter(
                parameters,
                "slowd_matype",
                default=0,
            )

            slowk, slowd = talib.STOCH(
                high,
                low,
                close,
                fastk_period=fastk_period,
                slowk_period=slowk_period,
                slowk_matype=slowk_matype,
                slowd_period=slowd_period,
                slowd_matype=slowd_matype,
            )

            return IndicatorResult(
                outputs={
                    "slowk": self._series(
                        timestamps,
                        slowk,
                    ),
                    "slowd": self._series(
                        timestamps,
                        slowd,
                    ),
                }
            )

        period = self._period(
            parameters,
            required=spec.id != "OBV",
        )

        if spec.id == "SMA":
            values = talib.SMA(
                close,
                timeperiod=period,
            )

        elif spec.id == "BBANDS":
            deviation = parameters.get(
                "deviation",
                2.0,
            )

            if not isinstance(
                deviation,
                (int, float),
            ) or isinstance(
                deviation,
                bool,
            ):
                raise ValueError("deviation must be numeric")

            if float(deviation) <= 0:
                raise ValueError("deviation must be greater than zero")

            upper, middle, lower = talib.BBANDS(
                close,
                timeperiod=period,
                nbdevup=float(deviation),
                nbdevdn=float(deviation),
                matype=0,
            )

            return IndicatorResult(
                outputs={
                    "upper": self._series(
                        timestamps,
                        upper,
                    ),
                    "middle": self._series(
                        timestamps,
                        middle,
                    ),
                    "lower": self._series(
                        timestamps,
                        lower,
                    ),
                }
            )

        elif spec.id == "EMA":
            values = talib.EMA(
                close,
                timeperiod=period,
            )

        elif spec.id == "RSI":
            values = talib.RSI(
                close,
                timeperiod=period,
            )

        elif spec.id == "ATR":
            values = talib.ATR(
                high,
                low,
                close,
                timeperiod=period,
            )

        elif spec.id == "MOMENTUM":
            values = talib.MOM(
                close,
                timeperiod=period,
            )

        elif spec.id == "ROC":
            values = talib.ROC(
                close,
                timeperiod=period,
            )

        elif spec.id == "OBV":
            values = talib.OBV(
                close,
                volume,
            )

        else:
            raise ValueError(f"TA-Lib provider does not support {spec.id}")

        return IndicatorResult(
            outputs={
                "value": TimeSeries(
                    timestamps=timestamps,
                    values=tuple(
                        None if not np.isfinite(value) else float(value) for value in values
                    ),
                )
            }
        )

    @staticmethod
    def _series(
        timestamps,
        values,
    ) -> TimeSeries:
        return TimeSeries(
            timestamps=timestamps,
            values=tuple(None if not np.isfinite(value) else float(value) for value in values),
        )

    @staticmethod
    def _matype_parameter(
        parameters: dict[str, float],
        name: str,
        *,
        default: int,
    ) -> int:
        value = parameters.get(name, default)

        if isinstance(value, bool):
            raise ValueError(  # noqa: TRY004
                f"{name} must be a non-negative integer"
            )

        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be a non-negative integer") from exc

        if not numeric.is_integer():
            raise ValueError(f"{name} must be a non-negative integer")

        matype = int(numeric)

        if matype < 0:
            raise ValueError(f"{name} must be a non-negative integer")

        return matype

    @staticmethod
    def _period_parameter(
        parameters: dict[str, float],
        name: str,
        *,
        default: int,
    ) -> int:
        value = parameters.get(name, default)

        if isinstance(value, bool):
            raise ValueError(  # noqa: TRY004
                f"{name} must be a positive integer"
            )

        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be a positive integer") from exc

        if not numeric.is_integer():
            raise ValueError(f"{name} must be a positive integer")

        period = int(numeric)

        if period <= 0:
            raise ValueError(f"{name} must be a positive integer")

        return period

    @staticmethod
    def _period(
        parameters: dict[str, float],
        *,
        required: bool,
    ) -> int:
        if "period" not in parameters:
            if required:
                raise ValueError("period parameter is required")

            return 0

        value = parameters["period"]

        if not float(value).is_integer():
            raise ValueError("period must be an integer")

        period = int(value)

        if period <= 0:
            raise ValueError("period must be greater than zero")

        return period
