"""
Unit tests for Component C — Train Model (modules/train_model.py).
"""

import pytest
from pathlib import Path
from modules.train_model import (
    Train,
    validate_train,
    load_trains_from_csv,
    generate_default_trains,
    TRAIN_SPEED_KMH,
    TRAIN_PRIORITY
)
from modules.network_model import create_railway_network


def test_train_creation_and_defaults():
    t = Train(
        train_id="T101",
        train_type="LOCAL",
        origin="CSMT",
        destination="Thane",
        scheduled_departure_min=0.0
    )
    assert t.train_id == "T101"
    assert t.speed_kmh() == 40.0
    assert t.get_priority() == 2
    assert t.dwell_min() == 1.0


def test_section_travel_time():
    t = Train("T101", "LOCAL", "CSMT", "Thane", 0.0, nominal_speed_kmph=40.0)
    section_attrs = {"distance_km": 4.0}
    # Travel time = (4.0 / 40.0) * 60 = 6.0 minutes
    assert t.section_travel_time(section_attrs) == 6.0

    t_fast = Train("T102", "FAST_LOCAL", "CSMT", "Thane", 0.0, nominal_speed_kmph=60.0)
    # Travel time = (5.0 / 60.0) * 60 = 5.0 minutes
    assert t_fast.section_travel_time({"distance_km": 5.0}) == 5.0


def test_train_invalid_type():
    with pytest.raises(ValueError, match="Invalid train_type"):
        Train("T999", "BULLET_TRAIN", "CSMT", "Thane", 0.0)


def test_train_invalid_departure():
    with pytest.raises(ValueError, match="scheduled_departure_min must be non-negative"):
        Train("T999", "LOCAL", "CSMT", "Thane", -5.0)


def test_train_invalid_speed():
    with pytest.raises(ValueError, match="nominal_speed_kmph must be positive"):
        Train("T999", "LOCAL", "CSMT", "Thane", 0.0, nominal_speed_kmph=-10.0)


def test_train_network_validation():
    net = create_railway_network()
    t_valid = Train("T101", "LOCAL", "CSMT", "Thane", 0.0)
    validate_train(t_valid, network=net)
    assert t_valid.route == ["CSMT", "Byculla", "Dadar", "Kurla", "Thane"]

    t_bad_origin = Train("T101", "LOCAL", "Kalyan", "Thane", 0.0)
    with pytest.raises(ValueError, match="origin 'Kalyan' does not exist"):
        validate_train(t_bad_origin, network=net)


def test_load_prototype_trains_csv():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "trains.csv"
    assert csv_path.exists()
    net = create_railway_network()
    trains = load_trains_from_csv(csv_path, network=net)
    assert len(trains) == 4
    assert [t.train_id for t in trains] == ["T101", "T102", "T103", "T104"]
    assert trains[0].train_type == "LOCAL"
    assert trains[1].train_type == "FAST_LOCAL"
    assert trains[2].train_type == "EXPRESS"
    assert trains[3].train_type == "LOCAL"


def test_generate_default_trains():
    net = create_railway_network()
    trains = generate_default_trains(net)
    assert len(trains) == 4
    assert trains[0].train_id == "T101"
    assert trains[0].route == ["CSMT", "Byculla", "Dadar", "Kurla", "Thane"]
