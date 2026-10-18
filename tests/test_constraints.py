"""
Unit tests for Component D — Operational Constraints (modules/constraints.py).
"""

import pytest
from modules.constraints import (
    SectionOccupancy,
    validate_static_constraints,
    simulate_schedule_feasibility
)
from modules.network_model import create_railway_network
from modules.train_model import Train, generate_default_trains


def test_section_occupancy_initialization():
    sec = SectionOccupancy(capacity=2, minimum_headway=2.0)
    assert sec.capacity == 2
    assert sec.minimum_headway == 2.0
    assert sec.last_entry_time() is None

    with pytest.raises(ValueError, match="capacity must be positive integer"):
        SectionOccupancy(capacity=0, minimum_headway=2.0)

    with pytest.raises(ValueError, match="minimum_headway must be positive"):
        SectionOccupancy(capacity=2, minimum_headway=-1.0)


def test_section_occupancy_headway_enforcement():
    # Headway = 2.0 min, Capacity = 2
    sec = SectionOccupancy(capacity=2, minimum_headway=2.0)

    # Train 1 enters at t = 0.0, exits at t = 6.0
    t1_entry, conflict1 = sec.earliest_feasible_entry(desired_entry=0.0, travel_time=6.0)
    assert t1_entry == 0.0
    assert not conflict1
    sec.register(0.0, 6.0, "T101")

    # Train 2 desires entry at t = 1.0 (headway violation)
    t2_entry, conflict2 = sec.earliest_feasible_entry(desired_entry=1.0, travel_time=6.0)
    assert conflict2
    assert t2_entry == 2.0  # Held until t=2.0 due to 2.0 min headway
    sec.register(t2_entry, t2_entry + 6.0, "T102")


def test_section_occupancy_capacity_enforcement():
    # Capacity = 2, Headway = 2.0 min
    sec = SectionOccupancy(capacity=2, minimum_headway=2.0)

    # T1 occupies [0.0, 10.0]
    sec.register(0.0, 10.0, "T101")
    # T2 occupies [2.0, 10.0]
    sec.register(2.0, 10.0, "T102")

    # Section has 2 occupants at t=5.0
    assert len(sec.occupants_at(5.0)) == 2

    # T3 desires entry at t = 4.0 (Headway from T2 would allow t=4.0, but section is full)
    t3_entry, conflict3 = sec.earliest_feasible_entry(desired_entry=4.0, travel_time=5.0)
    assert conflict3
    # Must wait until first occupant exits at t = 10.0
    assert t3_entry == 10.0


def test_validate_static_constraints_failures():
    net = create_railway_network()

    # Train with unknown station
    t_invalid = Train("T_BAD", "LOCAL", "UNKNOWN_STN", "Thane", 0.0)
    with pytest.raises(ValueError, match="origin 'UNKNOWN_STN' not in network"):
        validate_static_constraints(net, [t_invalid])


def test_simulate_schedule_feasibility():
    net = create_railway_network()
    trains = generate_default_trains(net)
    
    sim = simulate_schedule_feasibility(trains, net)
    assert "train_schedules" in sim
    assert "total_delay_min" in sim
    assert "conflicts_detected" in sim

    schedules = sim["train_schedules"]
    assert "T101" in schedules
    assert "T102" in schedules
    assert "T103" in schedules
    assert "T104" in schedules

    # Verify timeline stations
    t101_timeline = schedules["T101"]["timeline"]
    stations_visited = [stop["station"] for stop in t101_timeline]
    assert stations_visited == ["CSMT", "Byculla", "Dadar", "Kurla", "Thane"]
