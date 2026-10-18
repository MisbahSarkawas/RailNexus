# RailNexus Project Status

## Project Overview
- Research title: Maximizing Section Throughput Using AI-Powered Precise Train Traffic Control
- Framework: RailNexus — A Predictive Multi-Objective Framework for Railway Section Throughput Optimization
- Team: Misbah Sarkawas (Roll No. 112), Aliza Shaikh (Roll No. 114)
- Case study: Simplified Mumbai suburban corridor inspired by CSMT–Thane
- Data disclaimer: Section distances, minimum headways, platform counts, capacities, and train timetables used in this prototype are synthetic research assumptions, not official Indian Railways operational data.

## Global Status
- Current phase: Module 1 Completed & Verified
- Last verified update: 2026-10-18
- Integration status: Module 1 foundation fully implemented, tested, and ready. Integration with Module 2 and Module 3 remains pending a jointly agreed interface contract and canonical schema.
- Known project-wide issues: None

## Module 1 — Railway Section and Traffic Model
- Owner: Aliza Shaikh (Roll No. 114)
- Status: Implemented & Tested
- Implementation summary:
  - Station Model: Python dataclass, platform count validation, dwell-time validation, and CSV loader with strict input checking.
  - Network Model: Directed railway graph using NetworkX (`create_railway_network` preserved, `build_network_from_csv`), shortest path route resolution, and section decomposition.
  - Train Model: Train dataclass, nominal speeds (`LOCAL`: 40, `FAST_LOCAL`: 55, `EXPRESS`: 65, `FREIGHT`: 30 km/h), priorities, section travel time calculation (`(dist/speed)*60`), and schedule loading.
  - Operational Constraints: Deterministic `SectionOccupancy` headway and capacity tracker, static data validation, and multi-train schedule progression simulation.
  - Prototype CSV Data: Cleanly structured CSV files for stations, sections, and trains with complete validation.
  - End-to-End Pipeline: Runnable corridor simulation in `app.py`.
- Exact test command and actual results:
  - Command: `python -m pytest tests/ -v`
  - Result: 27 passed in 2.47s (Exit code 0).
    - `tests/test_constraints.py`: 5 passed
    - `tests/test_network_model.py`: 6 passed
    - `tests/test_station_model.py`: 8 passed
    - `tests/test_train_model.py`: 8 passed
- Exact application run command and actual result:
  - Command: `python app.py`
  - Result: Exited with code 0. Successfully loaded 5 stations, 4 sections, 4 trains, computed nominal travel times, and resolved 7 headway/capacity conflicts during simulated corridor transit (total schedule delay: 47.31 min).
- Dataset specifications:
  - `data/stations.csv`:
    - Row count: 5 rows
    - Schema: `station_id` (str), `name` (str), `station_type` (str), `platform_count` (int), `minimum_dwell_time_min` (float)
    - Records: CSMT (Terminus, 4 platforms), Byculla (Regular, 2 platforms), Dadar (Junction, 4 platforms), Kurla (Junction, 4 platforms), Thane (Terminus, 4 platforms)
    - Limitations: Prototype research assumptions for platform counts and dwell times.
  - `data/sections.csv`:
    - Row count: 4 rows
    - Schema: `section_id` (str), `start_station` (str), `end_station` (str), `distance_km` (float), `minimum_headway_min` (float), `capacity` (int)
    - Records: CSMT->Byculla (4 km, 2 min headway, cap 2), Byculla->Dadar (5 km, 2 min headway, cap 2), Dadar->Kurla (8 km, 3 min headway, cap 2), Kurla->Thane (17 km, 3 min headway, cap 2)
    - Limitations: Simplified directed linear corridor; does not model complex track crossovers or real-world signal blocks.
  - `data/trains.csv`:
    - Row count: 4 rows
    - Schema: `train_id` (str), `train_type` (str), `origin` (str), `destination` (str), `scheduled_departure_min` (float), `priority` (int), `nominal_speed_kmph` (float)
    - Records: T101 (LOCAL, dep 0.0m), T102 (FAST_LOCAL, dep 4.0m), T103 (EXPRESS, dep 7.0m), T104 (LOCAL, dep 10.0m)
    - Limitations: Synthetic sample schedule for prototype validation; not observed Mumbai suburban dispatch times.
- Known limitations:
  - Simplified linear one-way corridor topology (down-direction CSMT -> Thane).
  - Safety-critical signaling, interlocking, and block overlaps are outside this deterministic model.
- Next steps:
  - Maintain stable interfaces for Module 3 (Multi-Objective Optimizer).
  - Await joint agreement with Misbah on Module 2 prediction contract.

## Module 2 — Predictive Railway Intelligence
- Owner: Misbah Sarkawas (Roll No. 112)
- Development environment: Google Colab
- Status: Pending
- Notebook and model files: `RailNexus_Module2_Predictive_Intelligence.ipynb` (Colab exploratory phase)
- Data and preprocessing: Explored candidate timetable features (`train_info.csv` with 11,113 rows; `train_schedule.csv` with 186,074 rows); candidate delay dataset has only 10 rows; no model trained yet.
- Important note: Module 2 predictive modelling, exploratory notebooks, and datasets remain separate and are not modified by Module 1 tasks.
- Integration readiness: Awaiting model training, artifact export, or deterministic interface fixture.
- Known issues: Need to ensure cross-environment serialization compatibility between Colab (Python 3.13) and local Windows (Python 3.14).
- Next action: Develop reproducible feature extraction and agree on prediction output schema.

## Module 3 — Multi-Objective Traffic Optimizer
- Owner: Aliza Shaikh (Roll No. 114)
- Status: Pending
- Implemented features: Ready to build on Module 1's network graph, train models, and `SectionOccupancy` constraints.
- Tests and experiments: None
- Known issues: None
- Next action: Begin candidate strategy generation and objective formulation using Module 1 network foundation.

## Module 4 — Passenger Impact Intelligence
- Owner: Misbah Sarkawas (Roll No. 112)
- Status: Pending
- Implemented features: None
- Tests and experiments: None
- Known issues: None
- Next action: Awaiting passenger metrics formulation and demand interface.

## Module 5 — Experimental Research Framework
- Owner: Shared (Misbah Sarkawas & Aliza Shaikh)
- Status: Pending
- Baselines implemented: None
- Scenarios tested: None
- Metrics measured: None
- Result files: None
- Known issues: None
- Next action: Awaiting optimizer and prediction integration.

## Integration Checklist
- [x] Module 1 interfaces documented and unit-tested (27/27 passed).
- [x] Module 1 end-to-end corridor demonstration operational.
- [ ] Module 2 input/output contract agreed.
- [ ] Prediction model and preprocessing artefacts available.
- [ ] Module 3 constraints verified against optimizer candidate strategies.
- [ ] Passenger metrics connected to optimization evaluation.
- [ ] Baselines implemented and tested.
- [ ] Experimental scenarios reproducible.
- [ ] Results generated by actual executions.
- [ ] Final integrated prototype tested.

## Experimental Results
- Record only measured results.
- Include scenario, baseline, metric, units, and result-file path.
- Clearly distinguish assumptions, synthetic data, and measured outputs.
- No experimental optimization runs conducted yet.

## Known Issues and Decisions
- Decision: Confirmed single active project folder is `C:\Users\Aliza Shaikh\RailNexus`.
- Decision: Module 1 implemented strictly with standard library + `networkx`, `pandas`, `numpy`, and `pytest`.
- Decision: Prototype values explicitly separated from official Indian Railways data.
- Owner: Aliza Shaikh
- Next action: Handover complete for Module 1. Ready for Git status report synchronization.
