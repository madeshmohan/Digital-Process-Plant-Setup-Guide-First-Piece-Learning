# Plant Risk Register

| Risk ID | Risk Description | Cause | Impact | Likelihood | Severity | Mitigation Strategy | Owner | Monitoring Method |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **RSK-01** | Incorrect Parameter Entry | Operator typing error or misreading gauge | High | Medium | High | Automated validation engine with min/max bounds and interaction gating | Quality Lead | Real-time UI validation alerts |
| **RSK-02** | Sensor Calibration Drift | Machine sensor degradation over time | High | Medium | High | Machine maintenance signal tracking repeated parameter deviations | Maintenance Mgr | Automated maintenance signal logs |
| **RSK-03** | Wrong Product Variant Selection | Operator selects Variant A instead of Variant B | Critical | Low | High | Mandatory barcode/batch ID verification step before checklist start | Process Engineer | Batch log cross-reference |
| **RSK-04** | Interaction Envelope Violation | Temperature & pressure individually valid but jointly unstable | High | Medium | High | Non-linear interaction envelope calculation ($S_{int} \le 1.0$) blocking setup | Data Scientist | Validation audit trail |
| **RSK-05** | Offline Sync Data Loss | Browser cache clear before internet restoration | Medium | Low | Medium | Persistent SQLite LocalStorage backup & automatic sync trigger on reconnect | IT Ops | Sync queue counter check |
| **RSK-06** | Incorrect Recommendation | Biased historical data due to unrecorded defects | Medium | Low | Medium | Strict filtering (pass_fail=1 & status IN VALID/WARNING) + safety limit clamping | Data Scientist | Sample size & confidence score |
| **RSK-07** | Operator Step Bypass | Rushing setup without stabilization time | High | Medium | Medium | Step gating: step 8 cannot be checked until step 7 validation passes | Supervisor | Step duration timestamp audit |
| **RSK-08** | Database Corruption | Ungraceful shutdown or disk fault | High | Low | High | SQLite transaction write locks and periodic automated CSV backup export | SysAdmin | Daily CSV backup script |
| **RSK-09** | Maintenance-Related Parameter Drift | Hydraulic pressure valve leak or heating element wear | High | Medium | High | Automatic detection of 5+ parameter deviations triggering maintenance signal | Maintenance Lead | Maintenance dashboard alert |
| **RSK-10** | System Over-reliance | Operator trusting recommendations over physical safety signs | Critical | Low | Critical | Prominent safety disclaimer displayed on all UI screens & mandatory human oversight | EHS Lead | Annual EHS safety training |

---

> **Synthetic Prototype Data Disclaimer**
> Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results are synthetic demonstration assumptions and must not be used as real plant operating instructions.
