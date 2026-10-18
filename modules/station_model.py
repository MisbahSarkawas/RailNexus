"""
Module 1 — Railway Section and Traffic Model
Component B: Station Data Model and Validation.

Research Framework: RailNexus
Owner: Aliza Shaikh
Case Study: Simplified CSMT–Thane corridor

NOTE: Station attributes, platform counts, and minimum dwell times are
PROTOTYPE RESEARCH ASSUMPTIONS, not official Indian Railways operational data.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Union
import pandas as pd


@dataclass
class Station:
    """
    Represents a railway station node in the network.

    Attributes:
        station_id: Unique identifier for the station (e.g. 'CSMT').
        name: Human-readable station name.
        station_type: Classification (e.g., 'TERMINUS', 'JUNCTION', 'REGULAR').
        platform_count: Physical platforms at station (positive integer).
                        Note: Capacity depends on dwell time and scheduling,
                        not platform count alone.
        minimum_dwell_time_min: Minimum scheduled dwell time in minutes (>= 0).
    """
    station_id: str
    name: str
    station_type: str = "REGULAR"
    platform_count: int = 2
    minimum_dwell_time_min: float = 1.0

    def __post_init__(self):
        validate_station(self)


def validate_station(station: Station) -> None:
    """Validates individual station attributes against deterministic rules."""
    if not isinstance(station.station_id, str) or not station.station_id.strip():
        raise ValueError(f"Station station_id must be a non-empty string: {station.station_id!r}")
    if not isinstance(station.name, str) or not station.name.strip():
        raise ValueError(f"Station name must be a non-empty string for ID {station.station_id}: {station.name!r}")
    if not isinstance(station.platform_count, int) or station.platform_count <= 0:
        raise ValueError(
            f"Platform count for {station.station_id} must be a positive integer, got: {station.platform_count!r}"
        )
    if not isinstance(station.minimum_dwell_time_min, (int, float)) or station.minimum_dwell_time_min < 0:
        raise ValueError(
            f"Minimum dwell time for {station.station_id} must be a non-negative number (minutes), got: {station.minimum_dwell_time_min!r}"
        )


def load_stations_from_csv(csv_path: Union[str, Path]) -> Dict[str, Station]:
    """
    Loads and validates stations from a CSV file.

    Expected CSV columns:
        station_id,name,station_type,platform_count,minimum_dwell_time_min

    Returns:
        Dictionary mapping station_id (str) -> Station instance.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If required columns are missing, values are invalid, or duplicate IDs exist.
    """
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Stations CSV file not found: {path}")

    df = pd.read_csv(path)
    required_cols = {"station_id", "name", "station_type", "platform_count", "minimum_dwell_time_min"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Stations CSV missing required columns: {sorted(missing)}")

    if df.empty:
        raise ValueError("Stations CSV is empty.")

    # Check for duplicate station IDs
    duplicates = df[df["station_id"].duplicated(keep=False)]["station_id"].tolist()
    if duplicates:
        raise ValueError(f"Duplicate station_id found in {path}: {set(duplicates)}")

    stations: Dict[str, Station] = {}
    for idx, row in df.iterrows():
        sid = str(row["station_id"]).strip()
        sname = str(row["name"]).strip()
        stype = str(row["station_type"]).strip()
        
        try:
            pcount = int(row["platform_count"])
        except (ValueError, TypeError):
            raise ValueError(f"Invalid platform_count at row {idx} for station '{sid}': {row['platform_count']}")

        try:
            dwell = float(row["minimum_dwell_time_min"])
        except (ValueError, TypeError):
            raise ValueError(f"Invalid minimum_dwell_time_min at row {idx} for station '{sid}': {row['minimum_dwell_time_min']}")

        station = Station(
            station_id=sid,
            name=sname,
            station_type=stype,
            platform_count=pcount,
            minimum_dwell_time_min=dwell
        )
        stations[sid] = station

    return stations
