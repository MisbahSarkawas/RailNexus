"""
Unit tests for Component B — Station Model (modules/station_model.py).
"""

import pytest
from pathlib import Path
from modules.station_model import Station, load_stations_from_csv, validate_station


def test_station_creation_valid():
    station = Station(
        station_id="CSMT",
        name="Chhatrapati Shivaji Maharaj Terminus",
        station_type="TERMINUS",
        platform_count=4,
        minimum_dwell_time_min=2.0
    )
    assert station.station_id == "CSMT"
    assert station.name == "Chhatrapati Shivaji Maharaj Terminus"
    assert station.station_type == "TERMINUS"
    assert station.platform_count == 4
    assert station.minimum_dwell_time_min == 2.0


def test_station_invalid_id():
    with pytest.raises(ValueError, match="station_id must be a non-empty string"):
        Station(station_id="   ", name="Test")


def test_station_invalid_platform_count():
    with pytest.raises(ValueError, match="Platform count.*must be a positive integer"):
        Station(station_id="TEST", name="Test", platform_count=0)

    with pytest.raises(ValueError, match="Platform count.*must be a positive integer"):
        Station(station_id="TEST", name="Test", platform_count=-2)


def test_station_invalid_dwell_time():
    with pytest.raises(ValueError, match="Minimum dwell time.*must be a non-negative number"):
        Station(station_id="TEST", name="Test", minimum_dwell_time_min=-1.0)


def test_load_prototype_stations_csv():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "stations.csv"
    assert csv_path.exists(), f"Missing prototype dataset: {csv_path}"
    
    stations = load_stations_from_csv(csv_path)
    assert len(stations) == 5
    expected_ids = ["CSMT", "Byculla", "Dadar", "Kurla", "Thane"]
    assert list(stations.keys()) == expected_ids
    assert stations["CSMT"].platform_count == 4
    assert stations["Byculla"].minimum_dwell_time_min == 1.0


def test_load_stations_missing_file():
    with pytest.raises(FileNotFoundError):
        load_stations_from_csv("data/non_existent_stations.csv")


def test_load_stations_missing_columns(tmp_path):
    bad_csv = tmp_path / "bad_stations.csv"
    bad_csv.write_text("station_id,name\nCSMT,Terminus\n")
    with pytest.raises(ValueError, match="missing required columns"):
        load_stations_from_csv(bad_csv)


def test_load_stations_duplicate_ids(tmp_path):
    dup_csv = tmp_path / "dup_stations.csv"
    dup_csv.write_text(
        "station_id,name,station_type,platform_count,minimum_dwell_time_min\n"
        "CSMT,CSMT 1,REGULAR,2,1.0\n"
        "CSMT,CSMT 2,REGULAR,2,1.0\n"
    )
    with pytest.raises(ValueError, match="Duplicate station_id found"):
        load_stations_from_csv(dup_csv)
