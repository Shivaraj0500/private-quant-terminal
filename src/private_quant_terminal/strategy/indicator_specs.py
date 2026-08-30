from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class IndicatorParameterType(str, Enum):
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    ENUM = "ENUM"
    TIMEFRAME = "TIMEFRAME"


@dataclass(frozen=True)
class IndicatorParameterSpec:
    name: str
    parameter_type: IndicatorParameterType
    required: bool = False
    default: Any = None
    minimum: float | None = None
    maximum: float | None = None
    choices: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        name = self.name.strip()

        if not name:
            raise ValueError("Indicator parameter name cannot be empty.")

        object.__setattr__(self, "name", name)

        if self.parameter_type is IndicatorParameterType.ENUM:
            if not self.choices:
                raise ValueError(
                    "ENUM parameters require at least one choice."
                )

        elif self.choices:
            raise ValueError(
                "choices are only valid for ENUM parameters."
            )

        if (
            self.minimum is not None
            and self.maximum is not None
            and self.minimum > self.maximum
        ):
            raise ValueError(
                "minimum cannot be greater than maximum."
            )

        if self.required and self.default is not None:
            raise ValueError(
                "required parameters cannot define a default."
            )

    def validate(self, value: Any) -> None:
        parameter_type = self.parameter_type

        if parameter_type is IndicatorParameterType.INTEGER:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(
                    f"{self.name} must be an integer."
                )

        elif parameter_type is IndicatorParameterType.FLOAT:
            if isinstance(value, bool) or not isinstance(
                value,
                (int, float),
            ):
                raise ValueError(
                    f"{self.name} must be numeric."
                )

        elif parameter_type is IndicatorParameterType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValueError(
                    f"{self.name} must be boolean."
                )

        elif parameter_type in (
            IndicatorParameterType.STRING,
            IndicatorParameterType.TIMEFRAME,
        ):
            if not isinstance(value, str):
                raise ValueError(
                    f"{self.name} must be a string."
                )

        elif parameter_type is IndicatorParameterType.ENUM:
            if not isinstance(value, str):
                raise ValueError(
                    f"{self.name} must be a string."
                )

            if value not in self.choices:
                raise ValueError(
                    f"{self.name} must be one of {self.choices}."
                )

        if (
            self.minimum is not None
            and isinstance(value, (int, float))
            and value < self.minimum
        ):
            raise ValueError(
                f"{self.name} must be >= {self.minimum}."
            )

        if (
            self.maximum is not None
            and isinstance(value, (int, float))
            and value > self.maximum
        ):
            raise ValueError(
                f"{self.name} must be <= {self.maximum}."
            )


@dataclass(frozen=True)
class IndicatorOutputSpec:
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        name = self.name.strip()

        if not name:
            raise ValueError("Indicator output name cannot be empty.")

        object.__setattr__(self, "name", name)


@dataclass(frozen=True)
class IndicatorSpec:
    id: str
    version: str
    name: str
    category: str
    description: str
    parameters: tuple[IndicatorParameterSpec, ...]
    outputs: tuple[IndicatorOutputSpec, ...]
    warmup: int
    provider: str
    aliases: tuple[str, ...] = ()
    deterministic: bool = True

    def __post_init__(self) -> None:
        normalized_id = self.id.strip().upper()
        normalized_name = self.name.strip()

        if not normalized_id:
            raise ValueError("Indicator id cannot be empty.")

        if not self.version.strip():
            raise ValueError("Indicator version cannot be empty.")

        if not normalized_name:
            raise ValueError("Indicator name cannot be empty.")

        if not self.category.strip():
            raise ValueError("Indicator category cannot be empty.")

        if not self.provider.strip():
            raise ValueError("Indicator provider cannot be empty.")

        if self.warmup < 0:
            raise ValueError("Indicator warmup cannot be negative.")

        if not self.outputs:
            raise ValueError(
                "Indicator must define at least one output."
            )

        parameter_names = [
            parameter.name.lower()
            for parameter in self.parameters
        ]

        if len(parameter_names) != len(set(parameter_names)):
            raise ValueError(
                "Indicator parameter names must be unique."
            )

        output_names = [
            output.name.lower()
            for output in self.outputs
        ]

        if len(output_names) != len(set(output_names)):
            raise ValueError(
                "Indicator output names must be unique."
            )

        object.__setattr__(self, "id", normalized_id)

        aliases = tuple(
            alias.strip().upper()
            for alias in self.aliases
            if alias.strip()
        )

        object.__setattr__(self, "aliases", aliases)

    @property
    def identity(self) -> str:
        return f"{self.id}@{self.version}"

    def parameter(self, name: str) -> IndicatorParameterSpec:
        normalized = name.strip().lower()

        for parameter in self.parameters:
            if parameter.name.lower() == normalized:
                return parameter

        raise KeyError(
            f"Unknown indicator parameter: {name}"
        )

    def validate_parameters(
        self,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        known = {
            parameter.name: parameter
            for parameter in self.parameters
        }

        normalized: dict[str, Any] = {}

        for key, value in parameters.items():
            parameter = known.get(key)

            if parameter is None:
                raise ValueError(
                    f"Unknown parameter for {self.id}: {key}"
                )

            parameter.validate(value)
            normalized[key] = value

        for parameter in self.parameters:
            if parameter.name in normalized:
                continue

            if parameter.required:
                raise ValueError(
                    f"Missing required parameter: {parameter.name}"
                )

            if parameter.default is not None:
                normalized[parameter.name] = parameter.default

        return normalized