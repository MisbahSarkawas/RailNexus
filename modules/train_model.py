"""
Module 1 — Railway Section and Traffic Model
Component C: Train Data Model, Schedules, and Validation.

Research Framework: RailNexus
Owner: Aliza Shaikh
Case Study: Simplified CSMT–Thane corridor

NOTE: Train speeds, dwell times, priorities, and schedules are
PROTOTYPE RESEARCH ASSUMPTIONS, not official Indian Railways operational data.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
import networkx as nx
import pandas as pd

from modules.network_model import get_route, has_route


# Prototype Operating Speed Assumptions (km/h) by train type
TRAIN_SPEED_KMH: Dict[str, float] = {
    "LOCAL": 40.0,
    "FAST_LOCAL": 55.0,
    "EXPRESS": 65.0,
    "FREIGHT": 30.0,
}

# Prototype Intermediate Station Dwell Times (minutes)
DWELL_TIME_MIN: Dict[str, float] = {
    "LOCAL": 1.0,
    "FAST_LOCAL": 1.0,
    "EXPRESS": 0.5,
    "FREIGHT": 3.0,
}

# Prototype Scheduling Priority Weights (higher integer = higher scheduling priority)
TRAIN_PRIORITY: Dict[str, int] = {
    "EXPRESS": 4,
    "FAST_LOCAL": 3,
    "LOCAL": 2,
    "FREIGHT": 1,
}

ALLOWED_TRAIN_TYPES: Set[str] = set(TRAIN_SPEED_KMH.keys())


@dataclass
class Train:
    """
    Represents an individual train service scheduled on the network.

    Units:
        scheduled_departure_min: minutes from simulation start (t=0)
        nominal_speed_kmph: km/h
        dwell_time_min: minutes per intermediate station
    """
    train_id: str
    train_type: str
    origin: str
    destination: str
    scheduled_departure_min: float
    priority: int = 1
    nominal_speed_kmph: float = 40.0
    dwell_time_min: float = 1.0
    route: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Default speed and dwell time if matching standard prototype defaults
        if self.train_type in TRAIN_SPEED_KMH and (self.nominal_speed_kmph is None or self.nominal_speed_kmph == 40.0):
            self.nominal_speed_kmph = TRAIN_SPEED_KMH[self.train_type]
        if self.train_type in DWELL_TIME_MIN and self.dwell_time_min == 1.0:
            self.dwell_time_min = DWELL_TIME_MIN[self.train_type]
        if self.train_type in TRAIN_PRIORITY and self.priority == 1:
            self.priority = TRAIN_PRIORITY[self.train_type]

        validate_train(self)

    def speed_kmh(self) -> float:
        """Operating speed in km/h."""
        return float(self.nominal_speed_kmph)

    def dwell_min(self) -> float:
        """Station dwell time in minutes."""
        return float(self.dwell_time_min)

    def get_priority(self) -> int:
        """Scheduling priority weight."""
        return int(self.priority)

    def section_travel_time(self, section_attrs: Dict[str, Union[float, int]]) -> float:
        """
        Calculates time in minutes required to traverse a section at nominal speed.
        Travel time (min) = (Distance in km / Speed in km/h) * 60.0 min/h
        """
        distance_km = float(section_attrs["distance_km"])
        speed = self.speed_kmh()
        if speed <= 0:
            raise ValueError(f"Train {self.train_id} has invalid non-positive speed: {speed}")
        return (distance_km / speed) * 60.0


def validate_train(train: Train, network: Optional[nx.DiGraph] = None) -> None:
    """Validates train attributes against deterministic domain rules."""
    if not isinstance(train.train_id, str) or not train.train_id.strip():
        raise ValueError(f"Train train_id must be a non-empty string: {train.train_id!r}")

    if train.train_type not in ALLOWED_TRAIN_TYPES:
        raise ValueError(
            f"Invalid train_type '{train.train_type}' for train {train.train_id}. "
            f"Allowed types: {sorted(ALLOWED_TRAIN_TYPES)}"
        )

    if not isinstance(train.origin, str) or not train.origin.strip():
        raise ValueError(f"Train {train.train_id} origin must be a non-empty string.")

    if not isinstance(train.destination, str) or not train.destination.strip():
        raise ValueError(f"Train {train.train_id} destination must be a non-empty string.")

    if not isinstance(train.scheduled_departure_min, (int, float)) or train.scheduled_departure_min < 0:
        raise ValueError(
            f"Train {train.train_id} scheduled_departure_min must be non-negative, got: {train.scheduled_departure_min}"
        )

    if not isinstance(train.priority, int) or train.priority < 1:
        raise ValueError(f"Train {train.train_id} priority must be an integer >= 1, got: {train.priority}")

    if not isinstance(train.nominal_speed_kmph, (int, float)) or train.nominal_speed_kmph <= 0:
        raise ValueError(
            f"Train {train.train_id} nominal_speed_kmph must be positive number, got: {train.nominal_speed_kmph}"
        )

    if not isinstance(train.dwell_time_min, (int, float)) or train.dwell_time_min < 0:
        raise ValueError(
            f"Train {train.train_id} dwell_time_min must be non-negative, got: {train.dwell_time_min}"
        )

    if network is not None:
        if train.origin not in network:
            raise ValueError(f"Train {train.train_id} origin '{train.origin}' does not exist in network.")
        if train.destination not in network:
            raise ValueError(f"Train {train.train_id} destination '{train.destination}' does not exist in network.")
        if not has_route(network, train.origin, train.destination):
            raise ValueError(
                f"No route exists in network for train {train.train_id} from '{train.origin}' to '{train.destination}'."
            )
        if not train.route:
            train.route = get_route(network, train.origin, train.destination)


def load_trains_from_csv(
    csv_path: Union[str, Path],
    network: Optional[nx.DiGraph] = None
) -> List[Train]:
    """
    Loads and validates train records from CSV.

    Expected CSV columns:
        train_id,train_type,origin,destination,scheduled_departure_min,priority,nominal_speed_kmph
    """
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Trains CSV file not found: {path}")

    df = pd.read_csv(path)
    required_cols = {"train_id", "train_type", "origin", "destination", "scheduled_departure_min"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Trains CSV missing required columns: {sorted(missing)}")

    if df.empty:
        raise ValueError("Trains CSV is empty.")

    duplicates = df[df["train_id"].duplicated(keep=False)]["train_id"].tolist()
    if duplicates:
        raise ValueError(f"Duplicate train_id found in {path}: {set(duplicates)}")

    trains: List[Train] = []
    for idx, row in df.iterrows():
        tid = str(row["train_id"]).strip()
        ttype = str(row["train_type"]).strip()
        orig = str(row["origin"]).strip()
        dest = str(row["destination"]).strip()

        try:
            dep = float(row["scheduled_departure_min"])
        except (ValueError, TypeError):
            raise ValueError(f"Invalid scheduled_departure_min at row {idx} for train '{tid}': {row['scheduled_departure_min']}")

        prio = int(row["priority"]) if "priority" in row and pd.notna(row["priority"]) else TRAIN_PRIORITY.get(ttype, 1)
        speed = float(row["nominal_speed_kmph"]) if "nominal_speed_kmph" in row and pd.notna(row["nominal_speed_kmph"]) else TRAIN_SPEED_KMH.get(ttype, 40.0)
        dwell = float(row["dwell_time_min"]) if "dwell_time_min" in row and pd.notna(row["dwell_time_min"]) else DWELL_TIME_MIN.get(ttype, 1.0)

        route = get_route(network, orig, dest) if network is not None else []

        train = Train(
            train_id=tid,
            train_type=ttype,
            origin=orig,
            destination=dest,
            scheduled_departure_min=dep,
            priority=prio,
            nominal_speed_kmph=speed,
            dwell_time_min=dwell,
            route=route
        )
        if network is not None:
            validate_train(train, network=network)
        trains.append(train)

    return trains


def generate_default_trains(network: nx.DiGraph) -> List[Train]:
    """Generates the 4 canonical prototype trains (T101–T104) on CSMT -> Thane."""
    full_route = get_route(network, "CSMT", "Thane")
    trains = [
        Train("T101", "LOCAL", "CSMT", "Thane", 0.0, priority=2, nominal_speed_kmph=40.0, dwell_time_min=1.0, route=full_route),
        Train("T102", "FAST_LOCAL", "CSMT", "Thane", 4.0, priority=3, nominal_speed_kmph=55.0, dwell_time_min=1.0, route=full_route),
        Train("T103", "EXPRESS", "CSMT", "Thane", 7.0, priority=4, nominal_speed_kmph=65.0, dwell_time_min=0.5, route=full_route),
        Train("T104", "LOCAL", "CSMT", "Thane", 10.0, priority=2, nominal_speed_kmph=40.0, dwell_time_min=1.0, route=full_route),
    ]
    return trains
