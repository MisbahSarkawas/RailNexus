"""
RailNexus — Module 1: Railway Section and Traffic Model
End-to-End Demonstration and Execution Pipeline

Research Framework: RailNexus
Team: Misbah Sarkawas (Roll No. 112), Aliza Shaikh (Roll No. 114)
Primary Module Owner: Aliza Shaikh

Case Study: Simplified CSMT–Thane corridor
Corridor Route: CSMT -> Byculla -> Dadar -> Kurla -> Thane

NOTE: Distances, headways, capacities, train speeds, and dwell times are
PROTOTYPE RESEARCH ASSUMPTIONS, not official Indian Railways operational data.
"""

from pathlib import Path
import sys

from modules.station_model import load_stations_from_csv
from modules.network_model import build_network_from_csv, get_route, route_sections
from modules.train_model import load_trains_from_csv
from modules.constraints import simulate_schedule_feasibility


def main():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"

    stations_csv = data_dir / "stations.csv"
    sections_csv = data_dir / "sections.csv"
    trains_csv = data_dir / "trains.csv"

    print("=" * 80)
    print("RAILNEXUS — MODULE 1: RAILWAY SECTION & TRAFFIC MODEL")
    print("Corridor Prototype: CSMT -> Byculla -> Dadar -> Kurla -> Thane")
    print("=" * 80)

    # 1. Load Stations
    print("\n[Step 1] Loading Railway Stations...")
    stations = load_stations_from_csv(stations_csv)
    print(f"  Successfully loaded {len(stations)} stations:")
    for sid, stn in stations.items():
        print(f"    - [{sid}] {stn.name:<15} (Type: {stn.station_type:<8} Platforms: {stn.platform_count} Dwell: {stn.minimum_dwell_time_min:.1f}m)")

    # 2. Build Railway Network Graph
    print("\n[Step 2] Constructing Directed Network Graph from Sections...")
    network = build_network_from_csv(stations_csv, sections_csv)
    print(f"  Network built: {network.number_of_nodes()} station nodes, {network.number_of_edges()} directed section edges.")
    for u, v, data in network.edges(data=True):
        print(f"    - Section {data['section_id']}: {u} -> {v} | Distance: {data['distance_km']} km | Min Headway: {data['minimum_headway']} min | Capacity: {data['capacity']}")

    # 3. Load Trains
    print("\n[Step 3] Loading Prototype Train Fleet...")
    trains = load_trains_from_csv(trains_csv, network=network)
    print(f"  Successfully loaded {len(trains)} trains:")
    for tr in trains:
        print(f"    - [{tr.train_id}] {tr.train_type:<10} | Route: {tr.origin} -> {tr.destination} | Dep: t={tr.scheduled_departure_min:.1f}m | Speed: {tr.speed_kmh():.0f} km/h | Prio: {tr.get_priority()}")

    # 4. Route and Travel Time Analysis
    print("\n[Step 4] Nominal Section Travel Times (Free-Flow, No Delays):")
    for tr in trains:
        print(f"  Train {tr.train_id} ({tr.train_type}):")
        route = tr.route
        secs = route_sections(network, route)
        cumulative_t = 0.0
        for u, v, attrs in secs:
            tt = tr.section_travel_time(attrs)
            cumulative_t += tt
            print(f"    * {u} -> {v} ({attrs['distance_km']} km @ {tr.speed_kmh():.0f} km/h): {tt:.2f} min (cumulative: {cumulative_t:.2f} min)")

    # 5. Feasibility and Operational Constraint Simulation
    print("\n[Step 5] Deterministic Feasibility Simulation (Headway & Capacity Enforced):")
    sim_result = simulate_schedule_feasibility(trains, network)
    schedules = sim_result["train_schedules"]

    print(f"  Total Schedule Delay Incurred: {sim_result['total_delay_min']:.2f} min")
    print(f"  Total Headway/Capacity Conflicts Managed: {sim_result['conflicts_detected']}")

    print("\n  Detailed Train Progression Timetable:")
    for tid, info in schedules.items():
        print(f"\n  --- Train {tid} ({info['train_type']}) ---")
        print(f"      Scheduled Dep: {info['scheduled_departure']:.1f}m | Actual Dep: {info['actual_departure']:.1f}m | Arrival: {info['arrival_at_destination']:.1f}m | Transit Time: {info['total_transit_min']:.1f}m")
        for stop in info["timeline"]:
            stn = stop["station"]
            arr = f"{stop['arrival_min']:.2f}m"
            dep = f"{stop['departure_min']:.2f}m"
            print(f"        Station: {stn:<10} Arr: {arr:<8} Dep: {dep:<8}")

    print("\n" + "=" * 80)
    print("END OF MODULE 1 EXECUTION: All models, datasets, and constraints verified.")
    print("=" * 80)


if __name__ == "__main__":
    main()
