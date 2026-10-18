"""
Unit tests for Component A — Railway Network Model (modules/network_model.py).
"""

import pytest
from pathlib import Path
import networkx as nx
from modules.network_model import (
    create_railway_network,
    build_network_from_csv,
    get_route,
    has_route,
    get_section,
    route_sections,
    all_stations,
    validate_network
)


def test_create_railway_network_topology():
    net = create_railway_network()
    stations = all_stations(net)
    expected = ["CSMT", "Byculla", "Dadar", "Kurla", "Thane"]
    assert len(stations) == 5
    for s in expected:
        assert s in stations

    # Check edges
    assert net.number_of_edges() == 4
    sec_csmt_byculla = net.edges["CSMT", "Byculla"]
    assert sec_csmt_byculla["distance_km"] == 4.0
    assert sec_csmt_byculla["minimum_headway"] == 2.0
    assert sec_csmt_byculla["capacity"] == 2

    sec_kurla_thane = net.edges["Kurla", "Thane"]
    assert sec_kurla_thane["distance_km"] == 17.0
    assert sec_kurla_thane["minimum_headway"] == 3.0
    assert sec_kurla_thane["capacity"] == 2


def test_get_route_valid():
    net = create_railway_network()
    route = get_route(net, "CSMT", "Thane")
    assert route == ["CSMT", "Byculla", "Dadar", "Kurla", "Thane"]

    sub_route = get_route(net, "Byculla", "Kurla")
    assert sub_route == ["Byculla", "Dadar", "Kurla"]


def test_get_route_invalid_or_reverse():
    net = create_railway_network()
    # Reverse direction is not configured in one-way corridor
    assert not has_route(net, "Thane", "CSMT")
    with pytest.raises(ValueError, match="No directed route exists"):
        get_route(net, "Thane", "CSMT")

    with pytest.raises(ValueError, match="does not exist in network"):
        get_route(net, "Kalyan", "CSMT")


def test_get_section_and_route_sections():
    net = create_railway_network()
    sec = get_section(net, "Dadar", "Kurla")
    assert sec["distance_km"] == 8.0
    assert sec["minimum_headway"] == 3.0

    with pytest.raises(ValueError, match="No direct railway section exists"):
        get_section(net, "CSMT", "Kurla")

    route = ["CSMT", "Byculla", "Dadar"]
    r_secs = route_sections(net, route)
    assert len(r_secs) == 2
    assert r_secs[0][0] == "CSMT" and r_secs[0][1] == "Byculla"
    assert r_secs[1][0] == "Byculla" and r_secs[1][1] == "Dadar"


def test_build_network_from_csv():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    stn_csv = data_dir / "stations.csv"
    sec_csv = data_dir / "sections.csv"
    assert stn_csv.exists() and sec_csv.exists()

    net = build_network_from_csv(stn_csv, sec_csv)
    assert len(net.nodes) == 5
    assert len(net.edges) == 4
    assert net.nodes["CSMT"]["platform_count"] == 4
    assert net.edges["Byculla", "Dadar"]["distance_km"] == 5.0
    assert net.edges["Byculla", "Dadar"]["section_id"] == "SEC_BYCULLA_DADAR"


def test_validate_network_invalid_attributes():
    net = nx.DiGraph()
    net.add_node("A")
    net.add_node("B")
    net.add_edge("A", "B", distance_km=-5.0, minimum_headway=2.0, capacity=2)
    with pytest.raises(ValueError, match="invalid positive distance_km"):
        validate_network(net)

    net.edges["A", "B"]["distance_km"] = 5.0
    net.edges["A", "B"]["minimum_headway"] = 0.0
    with pytest.raises(ValueError, match="invalid positive minimum_headway"):
        validate_network(net)

    net.edges["A", "B"]["minimum_headway"] = 2.0
    net.edges["A", "B"]["capacity"] = -1
    with pytest.raises(ValueError, match="invalid positive integer capacity"):
        validate_network(net)
