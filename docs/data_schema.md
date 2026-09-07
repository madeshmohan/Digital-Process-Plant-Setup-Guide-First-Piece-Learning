# Database Schema & Data Dictionary

The SQLite database (`process_plant.db`) consists of 7 normalized relational tables.

## 1. `products`
- `product_id` (TEXT, PK): Unique product identifier (e.g. `PROD-A`).
- `product_variant` (TEXT, UNIQUE): Human readable name (e.g. `Variant A`).
- `product_family` (TEXT): Family classification (e.g. `Polymers`).
- `target_temperature` (REAL): Synthetic target temperature in °C.
- `min_temperature`, `max_temperature` (REAL): Allowed range.
- `target_pressure` (REAL): Synthetic target pressure in bar.
- `min_pressure`, `max_pressure` (REAL): Allowed range.

## 2. `setups`
- `setup_id` (TEXT, PK): Unique setup record code (e.g. `SET-1001`).
- `batch_id` (TEXT): Production batch code.
- `product_variant` (TEXT, FK): Target variant.
- `operator_id` (TEXT): Operator code (e.g. `OP-101`).
- `operator_experience_level` (TEXT): Novice, Intermediate, Expert.
- `machine_id` (TEXT): Equipment ID (e.g. `M01`).
- `shift` (TEXT): Morning, Evening, Night shift.
- `start_time`, `end_time` (TEXT): Timestamps.
- `setup_time_minutes` (REAL): Total duration.
- `is_prototype` (INTEGER): 0 = Manual Baseline, 1 = Digital Prototype.
- `final_status` (TEXT): Completed, Failed_Inspection.

## 3. `setup_parameters`
- `setup_id` (TEXT, PK, FK): Reference to `setups`.
- `temperature`, `pressure` (REAL): Actual parameters entered.
- `temperature_deviation`, `pressure_deviation` (REAL): Deviation from target.
- `interaction_score` (REAL): Calculated envelope score $S_{int}$.
- `validation_status` (TEXT): `VALID`, `WARNING`, `BLOCKED`.
- `heating_time`, `stabilization_time` (REAL): Minutes.

## 4. `setup_steps`
- `id` (INTEGER, PK AUTOINCREMENT)
- `setup_id` (TEXT, FK): Reference to `setups`.
- `step_id` (INTEGER): Step sequence (1 to 9).
- `step_name` (TEXT): Name of setup step.
- `step_completed` (INTEGER): 1 = Yes, 0 = No.
- `timestamp` (TEXT): Completion time.
- `duration_seconds` (INTEGER): Step duration.
- `notes` (TEXT): Operator comments.

## 5. `first_piece_inspection`
- `inspection_id` (TEXT, PK)
- `setup_id` (TEXT, FK UNIQUE)
- `inspection_time` (TEXT)
- `dimensional_quality` (REAL): Dimension deviation (mm).
- `surface_quality` (REAL): Score 1-10.
- `weight` (REAL): Weight in grams.
- `color_appearance` (TEXT): Normal, Discolored, Substandard.
- `process_quality_score` (REAL): 0 - 100.
- `defect_detected` (INTEGER): 1 = Yes, 0 = No.
- `defect_type` (TEXT): Category of defect.
- `pass_fail` (INTEGER): 1 = Pass, 0 = Fail.
- `inspector_comment` (TEXT)

## 6. `performance_metrics`
- `setup_id` (TEXT, PK, FK)
- `rework_required` (INTEGER): 1 = Yes, 0 = No.
- `material_waste_kg` (REAL): Scrap weight.
- `downtime_minutes` (REAL): Machine delay.
- `maintenance_flag` (INTEGER): 1 = Maintenance signal triggered.

## 7. `audit_logs`
- `log_id` (INTEGER, PK AUTOINCREMENT)
- `timestamp` (TEXT)
- `event_type` (TEXT): Log category.
- `user_or_system` (TEXT): Actor ID.
- `details` (TEXT): Description.

---

> **Synthetic Prototype Data Disclaimer**
> Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results are synthetic demonstration assumptions and must not be used as real plant operating instructions.
