# Experimental Baseline vs Prototype Performance Report

## Abstract

An experimental trial was conducted comparing traditional paper-based manual machine setup procedures (**Baseline**, $N = 340$) against the **Digital Setup Guide with Parameter Validation & Historical Learning** (**Prototype**, $N = 410$) across 750 synthetic setup runs across product Variants A, B, C, and D.

---

## 1. Comparative Performance Metrics

```text
Baseline vs Prototype Experiment

Metric                         Baseline    Prototype    Improvement
--------------------------------------------------------------------
Average Setup Time             42.01 min   26.50 min    36.92%
First-Piece Defect Rate        49.71%      8.05%        83.81%
Average Material Waste         4.61 kg     1.56 kg      66.16%
Rework Rate                    49.71%      8.05%        83.81%
```

| Metric | Manual Baseline | Digital Prototype | Absolute Change | Percentage Improvement |
| :--- | :---: | :---: | :---: | :---: |
| **Average Setup Duration** | 42.01 minutes | 26.50 minutes | -15.51 minutes | **36.92% Faster** |
| **First-Piece Defect Rate** | 49.71% | 8.05% | -41.66% | **83.81% Reduction** |
| **First-Piece Pass Rate** | 50.29% | 91.95% | +41.66% | **82.84% Increase** |
| **Rework Required Rate** | 49.71% | 8.05% | -41.66% | **83.81% Reduction** |
| **Average Material Waste per Setup** | 4.61 kg | 1.56 kg | -3.05 kg | **66.16% Waste Reduction** |
| **Blocked Out-of-Bounds Setups** | 0 (Manual) | 182 prevented | +182 blocked | **100% Interception** |

---

## 2. Key Findings & Insights

1. **Setup Time Reduction**:
   - The guided step-by-step checklist and recommended starting parameters eliminated operator guessing, reducing average setup duration by **36.92%** (from 42.01 mins down to 26.50 mins).
2. **Defect Rate Elimination**:
   - Enforcing individual parameter range limits and non-linear temperature-pressure interaction envelope ($S_{int} \le 1.0$) reduced first-piece scrap by **83.81%** (from 49.71% baseline defects down to 8.05%).
3. **Product Variant Performance**:
   - High-temperature variants (Variant C & Variant D) exhibited the largest quality gains due to tighter interaction tolerance enforcement.

---

## 3. Error Analysis Summary

Out of all recorded setup failures and blocked attempts:
- **Temperature-Pressure Interaction Violations**: 80.5%
- **Individual Pressure Range Violations**: 1.8%
- **Individual Temperature Range Violations**: 0.0%
- **Operator Step Deviations & Equipment Drift**: 7.0%
- **Other Material/Process Defects**: 10.6%

---

> **Synthetic Prototype Data Disclaimer**
> Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results are synthetic demonstration assumptions and must not be used as real plant operating instructions.
