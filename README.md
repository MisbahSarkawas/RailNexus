# RailNexus

**Research Framework:** RailNexus — A Predictive Multi-Objective Framework for Railway Section Throughput Optimization  
**Project Title:** Maximizing Section Throughput Using AI-Powered Precise Train Traffic Control  
**Academic Level:** Master of Computer Applications (MCA) Research Project  

**Team Members:**
- **Misbah Sarkawas** — Roll No. 112 (Module 2: Predictive Intelligence, Module 4: Passenger Impact)
- **Aliza Shaikh** — Roll No. 114 (Module 1: Railway Section & Traffic Model, Module 3: Multi-Objective Traffic Optimizer)

---

## 1. Project Overview

RailNexus investigates whether short-term predictions of railway traffic dynamics, section bottlenecks, and passenger demand can improve section-level train-control decisions without transferring delays or inconvenience across the railway corridor.

### Module 1: Railway Section and Traffic Model (Completed)
Module 1 serves as the deterministic, reusable foundation for the entire RailNexus framework. It models:
- Directed railway network graphs and physical topologies using NetworkX.
- Railway stations, platform configurations, and dwell-time assumptions.
- Directed railway sections with distances, minimum headways, and capacity limits.
- Heterogeneous train types (`LOCAL`, `FAST_LOCAL`, `EXPRESS`, `FREIGHT`), schedules, priorities, and nominal speeds.
- Deterministic static validation and time-dependent section occupancy/headway constraint tracking.

---

## 2. Corridor Case Study & Prototype Assumptions

The prototype models a simplified Mumbai suburban corridor inspired by the **CSMT–Thane** section on Central Railway:

$$\text{CSMT} \longrightarrow \text{Byculla} \longrightarrow \text{Dadar} \longrightarrow \text{Kurla} \longrightarrow \text{Thane}$$

> [!IMPORTANT]
> **Data Disclaimer:** Section distances, minimum headways, platform counts, capacities, and train timetables used in this prototype are **synthetic research assumptions** for controlled simulation. They do **not** represent official Indian Railways operational rules, signaling interlocks, or surveyed timetable statistics.

### Prototype Section Parameters

| Section ID | From | To | Distance (km) | Minimum Headway (min) | Prototype Capacity |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `SEC_CSMT_BYCULLA` | CSMT | Byculla | 4.0 | 2.0 | 2 |
| `SEC_BYCULLA_DADAR` | Byculla | Dadar | 5.0 | 2.0 | 2 |
| `SEC_DADAR_KURLA` | Dadar | Kurla | 8.0 | 3.0 | 2 |
| `SEC_KURLA_THANE` | Kurla | Thane | 17.0 | 3.0 | 2 |

### Prototype Train Fleet (Sample T101–T104)

| Train ID | Train Type | Origin | Destination | Scheduled Departure ($t=0$) | Nominal Speed | Dwell Time | Priority |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `T101` | `LOCAL` | CSMT | Thane | 0.0 min | 40 km/h | 1.0 min | 2 |
| `T102` | `FAST_LOCAL` | CSMT | Thane | 4.0 min | 55 km/h | 1.0 min | 3 |
| `T103` | `EXPRESS` | CSMT | Thane | 7.0 min | 65 km/h | 0.5 min | 4 |
| `T104` | `LOCAL` | CSMT | Thane | 10.0 min | 40 km/h | 1.0 min | 2 |

---

## 3. Architecture & Project Layout

```text
RailNexus/
├── app.py                      # Runnable end-to-end demonstration
├── requirements.txt            # Minimal core dependencies
├── PROJECT_STATUS.md           # Master status tracking across Modules 1–5
├── README.md                   # Project documentation and guide
├── modules/                    # Module 1 deterministic models
│   ├── __init__.py
│   ├── station_model.py        # Station dataclass, CSV loader, and validation
│   ├── network_model.py        # NetworkX directed graph, route & section helpers
│   ├── train_model.py          # Train dataclass, speeds, travel times, and CSV loader
│   └── constraints.py          # SectionOccupancy tracker & feasibility simulation
├── data/                       # Validated CSV datasets
│   ├── stations.csv            # 5 corridor stations
│   ├── sections.csv            # 4 directed sections
│   └── trains.csv              # Initial train fleet T101–T104
└── tests/                      # Automated pytest suite (27 tests)
    ├── test_station_model.py
    ├── test_network_model.py
    ├── test_train_model.py
    └── test_constraints.py
```

---

## 4. Installation & Environment Setup

### Prerequisites
- Python 3.10+ (tested and verified on Python 3.14.7)
- Windows PowerShell or compatible shell

### 1. Install Dependencies
```powershell
Set-Location -Path "C:\Users\Aliza Shaikh\RailNexus"
python -m pip install -r requirements.txt
```

### 2. Verify Installation
```powershell
python -c "import networkx, pandas, numpy, pytest; print('All dependencies imported successfully!')"
```

---

## 5. Running Tests & Demonstration

### Run All Automated Unit Tests
```powershell
python -m pytest tests/ -v
```
*(All 27 automated tests validate data parsing, negative constraint rejection, headway enforcement, capacity limits, and graph routing).*

### Run Individual Test Suites
```powershell
python -m pytest tests/test_station_model.py -v
python -m pytest tests/test_network_model.py -v
python -m pytest tests/test_train_model.py -v
python -m pytest tests/test_constraints.py -v
```

### Run End-to-End Corridor Demonstration
```powershell
python app.py
```
This loads the network from CSV, models nominal travel times, simulates headway and capacity constraints, and displays the full station-by-station train progression timetable.
