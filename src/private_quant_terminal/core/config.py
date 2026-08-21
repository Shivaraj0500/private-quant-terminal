from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Central application configuration."""

    project_name: str = "Private Quant Terminal"
    environment: str = "development"
    debug: bool = True
    data_dir: Path = Path("data")
    raw_data_dir: Path = Path("data/raw")
    processed_data_dir: Path = Path("data/processed")
    reports_dir: Path = Path("reports")


settings = Settings()
