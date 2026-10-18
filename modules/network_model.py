"""
Module 1 — Railway Section and Traffic Model
Component A: Railway Network Graph Model.

Research Framework: RailNexus
Owner: Aliza Shaikh
Case Study: Simplified CSMT–Thane corridor

NOTE: Section distances, minimum headways, and capacities are
PROTOTYPE RESEARCH ASSUMPTIONS, not official Indian Railways operational data.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Union
import networkx as nx
import pandas as pd

from modules.station_model import load_stations_from_csv


def create_railway_network() -> nx.DiGraph:
    """
    Builds the canonical prototype directed railway network graph.
    Preserves the original research topology and edge attributes.
    """
    network = nx.DiGraph()

    stations = [
        "CSMT",
        "Byculla",
        "Dadar",
        "Kurla",
        "Thane"
    ]

    for station in stations:
        network.add_node(station)

    sections = [
        ("CSMT", "Byculla", 4.0, 2.0, 2),
        ("Byculla", "Dadar", 5.0, 2.0, 2),
        ("Dadar", "Kurla", 8.0, 3.0, 2),
        ("Kurla", "Thane", 17.0, 3.0, 2)
    ]

    for start, end, distance, headway, capacity in sections:
        network.add_edge(
            start,
            end,
            distance_km=float(distance),
            minimum_headway=float(headway),
            capacity=int(capacity)
        )

    validate_network(network)
    return network


def build_network_from_csv(
    stations_csv: Union[str, Path],
    sections_csv: Union[str, Path]
) -> nx.DiGraph:
    """
    Builds a directed railway network from validated CSV files.

    Expected sections CSV columns:
        section_id,start_station,end_station,distance_km,minimum_headway_min,capacity
    """
    stations = load_stations_from_csv(stations_csv)
    
    sec_path = Path(sections_csv)
    if not sec_path.is_file():
        raise FileNotFoundError(f"Sections CSV file not found: {sec_path}")

    sec_df = pd.read_csv(sec_path)
    required_cols = {"section_id", "start_station", "end_station", "distance_km", "minimum_headway_min", "capacity"}
    missing = required_cols - set(sec_df.columns)
    if missing:
        raise ValueError(f"Sections CSV missing required columns: {sorted(missing)}")

    if sec_df.empty:
        raise ValueError("Sections CSV is empty.")

    network = nx.DiGraph()

    # Add station nodes with node attributes
    for sid, stn in stations.items():
        network.add_node(
            sid,
            name=stn.name,
            station_type=stn.station_type,
            platform_count=stn.platform_count,
            minimum_dwell_time_min=stn.minimum_dwell_time_min
        )

    # Check for duplicate section IDs
    sec_dups = sec_df[sec_df["section_id"].duplicated(keep=False)]["section_id"].tolist()
    if sec_dups:
        raise ValueError(f"Duplicate section_id found in {sec_path}: {set(sec_dups)}")

    # Add edges
    for idx, row in sec_df.iterrows():
        sec_id = str(row["section_id"]).strip()
        start = str(row["start_station"]).strip()
        end = str(row["end_station"]).strip()

        if start not in network.nodes:
            raise ValueError(f"Section {sec_id} references unknown start_station: '{start}'")
        if end not in network.nodes:
            raise ValueError(f"Section {sec_id} references unknown end_station: '{end}'")

        try:
            dist = float(row["distance_km"])
            if dist <= 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError(f"Section {sec_id} distance_km must be positive number, got: {row['distance_km']}")

        try:
            headway = float(row["minimum_headway_min"])
            if headway <= 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError(f"Section {sec_id} minimum_headway_min must be positive number, got: {row['minimum_headway_min']}")

        try:
            cap = int(row["capacity"])
            if cap <= 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError(f"Section {sec_id} capacity must be a positive integer, got: {row['capacity']}")

        network.add_edge(
            start,
            end,
            section_id=sec_id,
            distance_km=dist,
            minimum_headway=headway,
            capacity=cap
        )

    validate_network(network)
    return network


def validate_network(network: nx.DiGraph) -> None:
    """Validates structural integrity and physical edge attributes of the railway network."""
    if not isinstance(network, nx.DiGraph):
        raise TypeError(f"Railway network must be a networkx.DiGraph, got: {type(network)}")

    if len(network.nodes) == 0:
        raise ValueError("Railway network has no station nodes.")

    for u, v, data in network.edges(data=True):
        if "distance_km" not in data or data["distance_km"] <= 0:
            raise ValueError(f"Edge ({u}->{v}) missing or invalid positive distance_km: {data.get('distance_km')}")
        if "minimum_headway" not in data or data["minimum_headway"] <= 0:
            raise ValueError(f"Edge ({u}->{v}) missing or invalid positive minimum_headway: {data.get('minimum_headway')}")
        if "capacity" not in data or not isinstance(data["capacity"], int) or data["capacity"] <= 0:
            raise ValueError(f"Edge ({u}->{v}) missing or invalid positive integer capacity: {data.get('capacity')}")


def has_route(network: nx.DiGraph, origin: str, destination: str) -> bool:
    """Checks whether a directed path exists between origin and destination."""
    if origin not in network or destination not in network:
        return False
    return nx.has_path(network, origin, destination)


def get_route(network: nx.DiGraph, origin: str, destination: str) -> List[str]:
    """
    Returns the ordered list of stations from origin to destination.
    Raises ValueError if either station is missing or no path exists.
    """
    if origin not in network:
        raise ValueError(f"Origin station '{origin}' does not exist in network.")
    if destination not in network:
        raise ValueError(f"Destination station '{destination}' does not exist in network.")
    if not nx.has_path(network, origin, destination):
        raise ValueError(f"No directed route exists from '{origin}' to '{destination}'.")
    return nx.shortest_path(network, origin, destination)


def get_section(network: nx.DiGraph, from_station: str, to_station: str) -> Dict[str, Union[float, int, str]]:
    """Returns the section (edge) attribute dict between two adjacent stations."""
    if not network.has_edge(from_station, to_station):
        raise ValueError(f"No direct railway section exists between '{from_station}' and '{to_station}'.")
    return network.edges[from_station, to_station]


def route_sections(network: nx.DiGraph, route: List[str]) -> List[Tuple[str, str, Dict]]:
    """Given an ordered station route, returns list of (from_station, to_station, section_attrs)."""
    if len(route) < 2:
        return []
    result = []
    for a, b in zip(route, route[1:]):
        result.append((a, b, get_section(network, a, b)))
    return result


def all_stations(network: nx.DiGraph) -> List[str]:
    """Returns a list of all station IDs in the network."""
    return list(network.nodes)
