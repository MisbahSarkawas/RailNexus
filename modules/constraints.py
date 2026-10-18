"""
Module 1 — Railway Section and Traffic Model
Component D: Deterministic Operational Constraints and Feasibility Checking.

Research Framework: RailNexus
Owner: Aliza Shaikh
Case Study: Simplified CSMT–Thane corridor

NOTE: Operating constraints, headways, and capacity limits are
PROTOTYPE RESEARCH CONSTRAINTS, not official Indian Railways signalling or safety interlocking rules.
Real safety-critical signaling and interlocking are outside this deterministic prototype.
"""

from typing import Dict, List, Optional, Tuple, Union
import networkx as nx

from modules.network_model import get_section, has_route, route_sections
from modules.train_model import Train


class SectionOccupancy:
    """
    Tracks and enforces time-dependent entry, headway, and capacity constraints
    on an individual railway section.

    Two deterministic constraints are enforced:
      1. Minimum headway: Minimum time interval (minutes) between successive trains
         ENTERING the section.
      2. Capacity: Maximum simultaneous trains permitted in the section at any point in time.
    """

    def __init__(self, capacity: int, minimum_headway: float):
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError(f"Section capacity must be positive integer, got: {capacity}")
        if not isinstance(minimum_headway, (int, float)) or minimum_headway <= 0:
            raise ValueError(f"Section minimum_headway must be positive, got: {minimum_headway}")

        self.capacity: int = capacity
        self.minimum_headway: float = float(minimum_headway)
        self.events: List[Tuple[float, float, str]] = []  # List of (entry_time, exit_time, train_id)

    def last_entry_time(self) -> Optional[float]:
        """Returns the most recent train entry time, or None if no trains have entered."""
        if not self.events:
            return None
        return max(e[0] for e in self.events)

    def occupants_at(self, t: float) -> List[Tuple[float, float, str]]:
        """Returns all trains occupying the section at time t: [entry_time <= t < exit_time]."""
        return [e for e in self.events if e[0] <= t < e[1]]

    def earliest_feasible_entry(
        self,
        desired_entry: float,
        travel_time: float
    ) -> Tuple[float, bool]:
        """
        Determines the earliest feasible time a train can enter the section without
        violating the minimum headway or exceeding section capacity.

        Returns:
            Tuple[float, bool]: (feasible_entry_time, conflict_occurred)
        """
        if desired_entry < 0:
            raise ValueError(f"desired_entry time cannot be negative: {desired_entry}")
        if travel_time <= 0:
            raise ValueError(f"travel_time must be positive: {travel_time}")

        t = desired_entry
        conflict = False
        EPS = 1e-6
        MAX_ITERS = 1000

        for _ in range(MAX_ITERS):
            moved = False

            # 1. Enforce minimum headway constraint
            last_entry = self.last_entry_time()
            if last_entry is not None and (t - last_entry) < (self.minimum_headway - EPS):
                t = last_entry + self.minimum_headway
                conflict = True
                moved = True

            # 2. Enforce section capacity constraint
            occ = self.occupants_at(t)
            if len(occ) >= self.capacity:
                earliest_exit = min(e[1] for e in occ)
                new_t = max(t, earliest_exit)
                if new_t <= t:
                    new_t = t + EPS
                t = new_t
                conflict = True
                moved = True

            if not moved:
                break
        else:
            raise RuntimeError(
                f"earliest_feasible_entry failed to converge (t={t}, desired={desired_entry}, "
                f"capacity={self.capacity}, headway={self.minimum_headway})"
            )

        return round(t, 4), conflict

    def register(self, entry_time: float, exit_time: float, train_id: str) -> None:
        """Registers a completed entry/exit window for a train."""
        if exit_time <= entry_time:
            raise ValueError(f"exit_time ({exit_time}) must be strictly greater than entry_time ({entry_time})")
        self.events.append((entry_time, exit_time, train_id))


def validate_static_constraints(network: nx.DiGraph, trains: List[Train]) -> None:
    """
    Validates all static operational constraints before schedule execution:
      - All station references exist.
      - All train routes exist in the directed network.
      - Distances, headways, speeds, capacities are positive.
      - Dwell times and departure times are non-negative.
    """
    if not isinstance(network, nx.DiGraph):
        raise TypeError("network must be a networkx.DiGraph")
    if not trains:
        raise ValueError("Train list cannot be empty")

    for t in trains:
        if t.origin not in network:
            raise ValueError(f"Train {t.train_id} origin '{t.origin}' not in network.")
        if t.destination not in network:
            raise ValueError(f"Train {t.train_id} destination '{t.destination}' not in network.")
        if not has_route(network, t.origin, t.destination):
            raise ValueError(f"No route for train {t.train_id} from '{t.origin}' to '{t.destination}'.")
        if t.nominal_speed_kmph <= 0:
            raise ValueError(f"Train {t.train_id} speed must be positive: {t.nominal_speed_kmph}")
        if t.scheduled_departure_min < 0:
            raise ValueError(f"Train {t.train_id} scheduled departure cannot be negative: {t.scheduled_departure_min}")


def simulate_schedule_feasibility(
    trains: List[Train],
    network: nx.DiGraph
) -> Dict[str, Union[Dict, List, float]]:
    """
    Simulates train passage over the network respecting section headway and capacity.
    Calculates delays caused by infrastructure constraints.

    Returns:
        Summary dict containing:
          - 'train_schedules': detailed per-train arrival/departure timetable
          - 'total_delay_min': sum of delay across all trains
          - 'conflicts_detected': count of times a train had to hold/wait
    """
    validate_static_constraints(network, trains)

    # Initialize SectionOccupancy tracker for each edge in the network
    section_trackers: Dict[Tuple[str, str], SectionOccupancy] = {}
    for u, v, data in network.edges(data=True):
        section_trackers[(u, v)] = SectionOccupancy(
            capacity=data["capacity"],
            minimum_headway=data["minimum_headway"]
        )

    # Sort trains by scheduled departure time and priority
    sorted_trains = sorted(trains, key=lambda tr: (tr.scheduled_departure_min, -tr.priority))

    results = {}
    total_delay = 0.0
    total_conflicts = 0

    for tr in sorted_trains:
        current_time = float(tr.scheduled_departure_min)
        station_timeline = []
        route = tr.route if tr.route else nx.shortest_path(network, tr.origin, tr.destination)
        
        # Origin departure
        station_timeline.append({
            "station": route[0],
            "arrival_min": current_time,
            "departure_min": current_time
        })

        for u, v in zip(route, route[1:]):
            tracker = section_trackers[(u, v)]
            sec_attrs = get_section(network, u, v)
            travel_time = tr.section_travel_time(sec_attrs)

            # Check feasibility on section (u, v)
            feasible_entry, conflict = tracker.earliest_feasible_entry(current_time, travel_time)
            if conflict:
                total_conflicts += 1
                delay_incurred = feasible_entry - current_time
                total_delay += delay_incurred

            entry_t = feasible_entry
            exit_t = round(entry_t + travel_time, 4)
            tracker.register(entry_t, exit_t, tr.train_id)

            # At arrival station v:
            arrival_at_v = exit_t
            # If not the destination, train dwells
            dwell = tr.dwell_min() if v != route[-1] else 0.0
            dep_from_v = round(arrival_at_v + dwell, 4)

            station_timeline.append({
                "station": v,
                "arrival_min": arrival_at_v,
                "departure_min": dep_from_v
            })
            current_time = dep_from_v

        results[tr.train_id] = {
            "train_type": tr.train_type,
            "scheduled_departure": tr.scheduled_departure_min,
            "actual_departure": station_timeline[0]["departure_min"],
            "arrival_at_destination": station_timeline[-1]["arrival_min"],
            "total_transit_min": round(station_timeline[-1]["arrival_min"] - tr.scheduled_departure_min, 4),
            "timeline": station_timeline
        }

    return {
        "train_schedules": results,
        "total_delay_min": round(total_delay, 4),
        "conflicts_detected": total_conflicts
    }
