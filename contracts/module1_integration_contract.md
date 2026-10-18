# RailNexus — Module 1 Integration Contract & Data Interface Specification

**Research Framework:** RailNexus — A Predictive Multi-Objective Framework for Railway Section Throughput Optimization  
**Module:** Module 1 — Railway Section and Traffic Model  
**Module Owner & Author:** Aliza Shaikh (Roll No. 114)  
**Collaborator (Module 2 Owner):** Misbah Sarkawas (Roll No. 112)  
**Status:** Implemented Proposal for Multi-Module Integration  
**Date:** 2026-10-18  

---

## 1. Scope and Purpose

This contract establishes the deterministic data models, canonical schemas, units of measurement, and validation rules developed in **Module 1 (Railway Section and Traffic Model)**. It defines the stable boundary across which **Module 2 (Predictive Intelligence)** and **Module 3 (Multi-Objective Optimizer)** integrate with the railway network.

---

## 2. Canonical Identifiers and Corridor Definition

The prototype models the simplified CSMT–Thane corridor inspired by Mumbai suburban operations:

$$\text{CSMT} \longrightarrow \text{Byculla} \longrightarrow \text{Dadar} \longrightarrow \text{Kurla} \longrightarrow \text{Thane}$$

> [!NOTE]
> All distances, headways, capacities, speeds, and dwell times are **synthetic research assumptions** for controlled simulation and algorithm evaluation. They do not represent official Indian Railways operational rules.

### Canonical Identifiers:
- `station_id`: String (e.g., `"CSMT"`, `"Byculla"`, `"Dadar"`, `"Kurla"`, `"Thane"`). Case-sensitive, alphanumeric.
- `section_id`: String (e.g., `"SEC_CSMT_BYCULLA"`, `"SEC_BYCULLA_DADAR"`, `"SEC_DADAR_KURLA"`, `"SEC_KURLA_THANE"`).
- `train_id`: String (e.g., `"T101"`, `"T102"`, `"T103"`, `"T104"`).

---

## 3. Canonical Units Policy

To eliminate cross-module unit conversion errors, all RailNexus modules must adhere to the following standard units:

| Dimension | Canonical Unit | Abbreviation | Rule / Meaning |
| :--- | :--- | :---: | :--- |
| **Distance** | Kilometres | `km` | Positive floating-point value. |
| **Speed** | Kilometres per hour | `km/h` / `kmph` | Nominal cruising speed (> 0). |
| **Scheduled Time** | Minutes | `min` | Elapsed minutes from simulation start ($t=0.0 \ge 0$). |
| **Travel Time** | Minutes | `min` | $\text{Travel Time} = \left(\frac{\text{Distance}}{\text{Speed}}\right) \times 60.0$. |
| **Dwell Time** | Minutes | `min` | Scheduled dwell at intermediate stops ($\ge 0$). |
| **Headway** | Minutes | `min` | Minimum time interval between successive train entries (> 0). |
| **Delay** | Minutes | `min` | $\text{Delay} = \text{Actual Time} - \text{Scheduled Time} \ge 0$. |
| **Capacity** | Count | `integer` | Maximum simultaneous train occupancy per section ($\ge 1$). |

---

## 4. Module 1 Validated Schemas

### 4.1 Stations (`data/stations.csv`)
- **Row count:** 5
- **Schema:** `station_id,name,station_type,platform_count,minimum_dwell_time_min`

| Field | Type | Constraint | Example |
| :--- | :---: | :--- | :--- |
| `station_id` | `str` | Primary Key, non-empty | `"CSMT"` |
| `name` | `str` | Human-readable name | `"CSMT"` |
| `station_type` | `str` | `TERMINUS`, `JUNCTION`, `REGULAR` | `"TERMINUS"` |
| `platform_count` | `int` | Integer $\ge 1$ | `4` |
| `minimum_dwell_time_min` | `float` | Non-negative float | `2.0` |

### 4.2 Sections (`data/sections.csv`)
- **Row count:** 4
- **Schema:** `section_id,start_station,end_station,distance_km,minimum_headway_min,capacity`

| Field | Type | Constraint | Example |
| :--- | :---: | :--- | :--- |
| `section_id` | `str` | Primary Key, non-empty | `"SEC_CSMT_BYCULLA"` |
| `start_station` | `str` | Foreign Key $\to$ `stations.station_id` | `"CSMT"` |
| `end_station` | `str` | Foreign Key $\to$ `stations.station_id` | `"Byculla"` |
| `distance_km` | `float` | Float $> 0$ | `4.0` |
| `minimum_headway_min` | `float` | Float $> 0$ | `2.0` |
| `capacity` | `int` | Integer $\ge 1$ | `2` |

### 4.3 Trains (`data/trains.csv`)
- **Row count:** 4
- **Schema:** `train_id,train_type,origin,destination,scheduled_departure_min,priority,nominal_speed_kmph`

| Field | Type | Constraint | Example |
| :--- | :---: | :--- | :--- |
| `train_id` | `str` | Primary Key, non-empty | `"T101"` |
| `train_type` | `str` | `LOCAL`, `FAST_LOCAL`, `EXPRESS`, `FREIGHT` | `"LOCAL"` |
| `origin` | `str` | Must exist in network | `"CSMT"` |
| `destination` | `str` | Must exist in network | `"Thane"` |
| `scheduled_departure_min` | `float` | Non-negative float | `0.0` |
| `priority` | `int` | Integer $\ge 1$ (higher = goes first) | `2` |
| `nominal_speed_kmph` | `float` | Float $> 0$ | `40.0` |

---

## 5. Integration Interface for Module 2 (Predictive Intelligence)

### 5.1 Infrastructure Inputs Provided by Module 1:
Module 1 provides deterministic getters and schedule projections:
- `modules.network_model.get_route(network, origin, destination)` $\to$ `List[str]`
- `modules.network_model.get_section(network, from_station, to_station)` $\to$ `Dict`
- `modules.train_model.Train.section_travel_time(section_attrs)` $\to$ `float`
- `modules.constraints.SectionOccupancy` $\to$ deterministic headway and capacity verification.

### 5.2 Proposed Feature DataFrame for Module 2 Predictions:
When predicting short-term delay or section bottlenecks, input records should include:
- `train_id`: String
- `train_type`: String (`LOCAL`, `FAST_LOCAL`, etc.)
- `station_id` / `section_id`: String
- `scheduled_departure_min`: Float
- `nominal_speed_kmph`: Float
- `scheduled_entry_min`: Float
- `scheduled_exit_min`: Float

### 5.3 Proposed Output Interface from Module 2 (To be finalized jointly with Misbah):
- `train_id`: String
- `section_id` / `station_id`: String
- `predicted_delay_min`: Float ($\ge 0.0$)
- `prediction_horizon_min`: Float
- `confidence_score`: Float ($0.0 \le c \le 1.0$)
- `model_version`: String

> [!IMPORTANT]
> **Data Separation Rule:** Module 1 deterministic models must not depend on Colab notebook variables, unverified nationwide delay datasets, or synthetic delay labels. All predictive models in Module 2 will consume Module 1 inputs through this documented schema.
