# Process Plant Digital Setup Guide MVP

**Digital Setup Guide with Parameter Validation, Non-Linear Interaction Envelope, and First-Piece Learning**

---

> ⚠️ **SYNTHETIC PROTOTYPE DATA DISCLAIMER**  
> Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results are synthetic demonstration assumptions and must not be used as real plant operating instructions. Actual plant operating limits must be defined, verified, approved, and maintained by qualified process, safety, quality, and maintenance personnel.

---

## 1. Project Overview

In process manufacturing plants where product quality depends strongly on interacting **temperature and pressure conditions**, manual setup instructions can vary significantly between operators. This inconsistency causes:

* Incorrect machine setups and out-of-envelope parameter combinations.
* Avoidable first-piece defects and material scrap waste.
* Longer setup changeover times and high rework rates.
* Accelerated machine wear due to improper operating stresses.

This repository provides a functional, end-to-end local MVP containing:
1. **Digital Setup Guide**: Step-by-step operator checklist with gated progression.
2. **Parameter Validation Engine**: Evaluates individual limits AND non-linear temperature-pressure interaction envelope ($S_{int} = x^2 + y^2 + 0.6xy \le 1.0$).
3. **Interactive 2D Envelope Visualizer**: Live canvas/SVG plot showing target point, safe operating region, warning zone, and real-time operator settings.
4. **First-Piece Quality Inspection & Learning**: Captures physical measurements and calculates historical parameter recommendations ($T_{rec}, P_{rec}$) from past successful setups, clamped strictly within safety bounds.
5. **Offline Mode & Synchronization**: Caches setup records locally when offline and syncs with SQLite when connectivity is restored, with idempotency and duplicate prevention.
6. **Management Dashboard & Baseline Experiment**: Compares traditional manual setups against prototype performance metrics directly from the SQLite database across 750 setup records.

---

## 2. Features

- **Field-Friendly UI**: Large touch controls, auto-timestamping, step gating if parameter validation is `BLOCKED`.
- **Non-Linear Interaction Validation**: Detects cases where temperature and pressure are individually valid but jointly violate thermal-pressure stress envelopes.
- **Three Demonstrated Failure Presets**:
  - Failure 1 (Temp Out of Range): Variant A, $T = 230^\circ\text{C} \rightarrow$ `BLOCKED`.
  - Failure 2 (Pressure Out of Range): Variant A, $P = 4.2\text{ bar} \rightarrow$ `BLOCKED`.
  - Failure 3 (Interaction Violation): Variant A, $T = 184^\circ\text{C}, P = 5.28\text{ bar} \rightarrow$ `BLOCKED` (individually valid ranges, $S_{int} = 1.96 > 1.0$).
- **Condition Maintenance Signals**: Flags machines with repeated parameter deviations (e.g. Machine M01 pressure drift).
- **Offline Synchronization**: Idempotent queue sync with retry handling and client setup ID mapping.
- **Audit Logging**: Comprehensive event trail stored in SQLite.

---

## 3. Architecture

The application is built on a lightweight, local-first architecture designed to run on a standard laptop without cloud infrastructure or paid third-party services:

- **Backend**: Python 3.10+, FastAPI, Uvicorn, SQLite database (`process_plant.db`).
- **Frontend**: Lightweight React Single Page Application (SPA) served via Python static HTTP server (`serve_frontend.py` on port 5173).
- **Analytics & Data**: Pandas, NumPy, Pytest.

```text
Operator
  ↓
React SPA UI (http://localhost:5173)
  ↓
LocalStorage Offline Queue (Sync retry buffer)
  ↓
FastAPI Backend (http://localhost:8000)
  ↓
Parameter Validation Engine (Range & Interaction envelope)
  ↓
SQLite Database (process_plant.db)
  ↓
Historical Recommendation Engine & Management Dashboard
```

---

## 4. Reproducible Setup & Execution Instructions

### Step 1: Install Dependencies

```bash
py -3 -m pip install -r requirements.txt
```

---

### Step 2: Initialize Database & Generate Synthetic Dataset

Generates 750 realistic setup and inspection records in SQLite (`process_plant.db`):

```bash
$env:PYTHONPATH="."; py -3 -m data.generate_dataset
```

---

### Step 3: Run Automated Tests

Execute the test suite (18 automated tests covering validation logic, interaction bounds, recommendations, failure presets, offline sync, and duplicate prevention):

```bash
$env:PYTHONPATH="."; py -3 -m pytest
```

---

### Step 4: Run Analytics & Reproduce Baseline Experiment

Generate the exact baseline vs. prototype metrics directly from the database:

```bash
$env:PYTHONPATH="."; py -3 analytics/experiment.py
```

---

### Step 5: Start Backend REST API Server

```bash
$env:PYTHONPATH="."; py -3 backend/main.py
```

- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Documentation: `http://localhost:8000/docs`

---

### Step 6: Start Frontend Server

In a separate terminal:

```bash
py -3 serve_frontend.py
```

- Frontend URL: `http://localhost:5173`

---

## 5. Measured Baseline vs Prototype Experiment Results

Calculated directly from the 750-record database dataset:

```text
Baseline vs Prototype Experiment

Metric                         Baseline    Prototype    Improvement
--------------------------------------------------------------------
Average Setup Time             42.01 min   26.50 min    36.92%
First-Piece Defect Rate        49.71%      8.05%        83.81%
Average Material Waste         4.61 kg     1.56 kg      66.16%
Rework Rate                    49.71%      8.05%        83.81%
```

| Metric | Manual Baseline | Digital Prototype | Absolute Change | Improvement |
| :--- | :---: | :---: | :---: | :---: |
| **Total Setups Analyzed** | 340 setups | 410 setups | 750 total | - |
| **Average Setup Duration** | 42.01 minutes | 26.50 minutes | -15.51 mins | **36.92% Faster** |
| **First-Piece Defect Rate** | 49.71% | 8.05% | -41.66% | **83.81% Reduction** |
| **Average Scrap Material Waste** | 4.61 kg | 1.56 kg | -3.05 kg | **66.16% Reduction** |
| **Rework Required Rate** | 49.71% | 8.05% | -41.66% | **83.81% Reduction** |
| **Blocked Out-of-Bounds Setups** | 0 (Manual) | 182 blocked | +182 blocked | **100% Interception** |
