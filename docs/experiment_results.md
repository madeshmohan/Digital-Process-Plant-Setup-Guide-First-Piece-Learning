# Experimental Baseline vs Prototype Performance Report & Simulation Benchmark

## Abstract

An experimental trial and simulation benchmark was conducted comparing traditional paper-based manual machine setup procedures (**Baseline**, $N = 340$) against the **Digital Setup Guide with Parameter Validation & Historical Learning** (**Prototype**, $N = 410$) across 750 synthetic setup runs across product Variants A, B, C, and D.

---

## 1. Primary Empirical Dataset Performance Metrics

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

## 2. Quantified Multi-Run Simulation Benchmark & Statistical Bounds

To establish a verifiable benchmark for subsequent academic and industrial reviews, Monte Carlo simulation experiments were conducted across sample sizes $N \in \{100, 250, 500, 750, 1000\}$ iterations.

| Sample Size ($N$) | Metric | Baseline (Mean $\pm$ SD / 95% CI) | Prototype (Mean $\pm$ SD / 95% CI) | Improvement |
| :---: | :--- | :---: | :---: | :---: |
| **$N=100$** | Setup Duration (min) | $43.89 \pm 4.59$ min | $27.24 \pm 3.31$ min | **37.93% Faster** |
| | First-Piece Defect Rate | $42.00\% \pm 9.67\%$ | $3.00\% \pm 3.34\%$ | **92.86% Reduction** |
| | Material Waste (kg) | $4.26 \text{ kg}$ | $1.21 \text{ kg}$ | **71.71% Reduction** |
| **$N=250$** | Setup Duration (min) | $43.59 \pm 4.67$ min | $27.85 \pm 3.22$ min | **36.12% Faster** |
| | First-Piece Defect Rate | $52.80\% \pm 6.19\%$ | $3.20\% \pm 2.18\%$ | **93.94% Reduction** |
| | Material Waste (kg) | $4.70 \text{ kg}$ | $1.25 \text{ kg}$ | **73.42% Reduction** |
| **$N=500$** | Setup Duration (min) | $43.60 \pm 4.80$ min | $27.74 \pm 3.27$ min | **36.39% Faster** |
| | First-Piece Defect Rate | $53.20\% \pm 4.37\%$ | $4.80\% \pm 1.87\%$ | **90.98% Reduction** |
| | Material Waste (kg) | $4.96 \text{ kg}$ | $1.32 \text{ kg}$ | **73.33% Reduction** |
| **$N=750$** | Setup Duration (min) | $43.22 \pm 4.92$ min | $27.40 \pm 3.17$ min | **36.60% Faster** |
| | First-Piece Defect Rate | $54.53\% \pm 3.56\%$ | $4.53\% \pm 1.49\%$ | **91.69% Reduction** |
| | Material Waste (kg) | $4.97 \text{ kg}$ | $1.32 \text{ kg}$ | **73.41% Reduction** |
| **$N=1000$** | Setup Duration (min) | $43.47 \pm 4.99$ min | $27.68 \pm 3.24$ min | **36.33% Faster** |
| | First-Piece Defect Rate | $54.70\% \pm 3.09\%$ | $4.80\% \pm 1.32\%$ | **91.22% Reduction** |
| | Material Waste (kg) | $4.98 \text{ kg}$ | $1.36 \text{ kg}$ | **72.80% Reduction** |

---

## 3. Key Findings & Insights

1. **Setup Time Reduction**:
   - The guided step-by-step checklist and recommended starting parameters eliminated operator guessing, reducing average setup duration by **36.92%** (from 42.01 mins down to 26.50 mins).
2. **Defect Rate Elimination**:
   - Enforcing individual parameter range limits and non-linear temperature-pressure interaction envelope ($\Phi(T, P) \le 1.00$) reduced first-piece scrap by **83.81%** (from 49.71% baseline defects down to 8.05%).
3. **Product Variant Performance**:
   - High-temperature variants (Variant C & Variant D) exhibited the largest quality gains due to tighter interaction tolerance enforcement.

---

## 4. Error Analysis Summary

Out of all recorded setup failures and blocked attempts:
- **Temperature-Pressure Interaction Violations**: 80.5%
- **Individual Pressure Range Violations**: 1.8%
- **Individual Temperature Range Violations**: 0.0%
- **Operator Step Deviations & Equipment Drift**: 7.0%
- **Other Material/Process Defects**: 10.6%

---

> **Synthetic Prototype Data Disclaimer**  
> Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results are synthetic demonstration assumptions and must not be used as real plant operating instructions.
