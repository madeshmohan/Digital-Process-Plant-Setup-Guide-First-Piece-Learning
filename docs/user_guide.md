# Operator & Manager User Guide

Welcome to the **Process Plant Digital Setup Guide**. This application helps machine operators set up production equipment accurately, validate interacting temperature and pressure parameters, inspect first-piece quality, and learn from historical best practices.

---

## 1. How to Perform a Machine Setup (Operator Workflow)

1. Open the application at `http://localhost:5173`.
2. Click on the **Setup Guide** tab.
3. Select your **Product Variant** (Variant A, B, C, or D), enter your Batch ID, Machine ID, and Operator ID.
4. Click **Start New Setup**.
5. Work through the 9 setup checklist steps:
   - Step 1: Inspect machine condition.
   - Step 2: Clean required contact surfaces.
   - Step 3: Load required raw material.
   - Step 4: Set target temperature (°C).
   - Step 5: Set target pressure (bar).
   - Step 6: Wait for thermal & pressure stabilization.
   - Step 7: Verify actual parameters. *(Triggers Parameter Validation)*.
   - Step 8: Run trial setup.
   - Step 9: First-piece inspection.
6. Observe the **Validation Indicator**:
   - **GREEN (VALID)**: Parameters and interaction envelope are within valid operating window. Proceed to next step.
   - **YELLOW (WARNING)**: Parameters are within limits but near operating boundary. Exercise caution.
   - **RED (BLOCKED)**: Parameters or interaction score violate safe limits. Read the explanation and correct inputs before proceeding.

---

## 2. Performing First-Piece Inspection

1. After completing parameter verification, navigate to the **First-Piece Inspection** step or tab.
2. Enter measurement values (Dimensional deviation, Surface score, Weight, Color/Appearance).
3. If defects are observed:
   - Check **Defect Detected**.
   - Select the **Defect Type** (e.g. `dimensional_variation`, `discoloration`, `interaction_stress_defect`).
   - Add comments.
4. Click **Submit First-Piece Result**.

---

## 3. Using Historical Recommendations

- Click **Get Recommended Parameters** during setup to view statistical baseline suggestions derived from past successful setups.
- Recommendations display sample size, historical pass rate, and confidence levels.
- Recommendations **never** override configured safety boundaries.

---

## 4. Working Offline and Data Synchronization

- If internet connectivity drops, the top bar displays **OFFLINE MODE (Data stored locally)**.
- Continue completing setups normally; setups are saved in local storage queue.
- When connection returns, click **Sync Data** to upload pending records to the backend database.

---

## 5. Management Dashboard & Error Analysis

- Click the **Management Dashboard** tab to view setup time improvements, defect reduction rates, error classification breakdown, and maintenance signals.

---

> **Synthetic Prototype Data Disclaimer**
> Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results are synthetic demonstration assumptions and must not be used as real plant operating instructions.
