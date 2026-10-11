import math
import random
import numpy as np
import json
import os
from typing import Dict, Any, List
from backend.validation.validation_engine import PRODUCT_SPECS, validate_parameters

SAFETY_DISCLAIMER = (
    "Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results "
    "are synthetic demonstration assumptions and must not be used as real plant operating instructions."
)

def run_simulation_benchmark(sample_sizes: List[int] = [100, 250, 500, 750, 1000]) -> Dict[str, Any]:
    """
    Quantifies baseline vs prototype setup metrics across simulated runs to establish a verifiable benchmark.
    Computes mean, standard deviation, and 95% confidence intervals for setup time and defect rate.
    """
    np.random.seed(42)
    random.seed(42)
    
    variants = list(PRODUCT_SPECS.keys())
    benchmark_results = []

    for N in sample_sizes:
        b_times = []
        p_times = []
        b_defects = []
        p_defects = []
        b_wastes = []
        p_wastes = []

        for i in range(N):
            variant = random.choice(variants)
            spec = PRODUCT_SPECS[variant]

            # --- BASELINE SIMULATION (Unvalidated Manual Setup) ---
            t_noise_b = np.random.normal(0, 3.8)
            p_noise_b = np.random.normal(0, 0.28)
            actual_t_b = spec["target_temperature"] + t_noise_b
            actual_p_b = spec["target_pressure"] + p_noise_b

            val_b = validate_parameters(variant, actual_t_b, actual_p_b)
            # Baseline setup duration: 35-55 mins
            time_b = float(random.uniform(35.0, 52.0))
            b_times.append(time_b)

            # Baseline defect probability based on validation status
            if val_b["status"] == "VALID":
                fail_p = 0.12
            elif val_b["status"] == "WARNING":
                fail_p = 0.45
            else:
                fail_p = 0.92

            is_defect_b = 1 if random.random() < fail_p else 0
            b_defects.append(is_defect_b)
            b_wastes.append(float(random.uniform(4.5, 12.0) if is_defect_b else random.uniform(0.5, 1.5)))

            # --- PROTOTYPE SIMULATION (Guided Interaction Validation) ---
            t_noise_p = np.random.normal(0, 1.1)
            p_noise_p = np.random.normal(0, 0.08)
            actual_t_p = spec["target_temperature"] + t_noise_p
            actual_p_p = spec["target_pressure"] + p_noise_p

            val_p = validate_parameters(variant, actual_t_p, actual_p_p)
            time_p = float(random.uniform(22.0, 33.0))
            p_times.append(time_p)

            if val_p["status"] == "VALID":
                fail_p_proto = 0.04
            elif val_p["status"] == "WARNING":
                fail_p_proto = 0.25
            else:
                fail_p_proto = 0.92

            is_defect_p = 1 if random.random() < fail_p_proto else 0
            p_defects.append(is_defect_p)
            p_wastes.append(float(random.uniform(4.5, 12.0) if is_defect_p else random.uniform(0.5, 1.5)))

        # Statistical calculations
        b_time_mean = float(np.mean(b_times))
        b_time_std = float(np.std(b_times))
        p_time_mean = float(np.mean(p_times))
        p_time_std = float(np.std(p_times))
        time_improvement = float(((b_time_mean - p_time_mean) / b_time_mean) * 100.0)

        b_defect_rate = float(np.mean(b_defects) * 100.0)
        p_defect_rate = float(np.mean(p_defects) * 100.0)
        defect_reduction = float(((b_defect_rate - p_defect_rate) / b_defect_rate) * 100.0) if b_defect_rate > 0 else 0.0

        # 95% Confidence Interval for defect rates
        b_ci = 1.96 * math.sqrt((b_defect_rate / 100.0) * (1 - b_defect_rate / 100.0) / N) * 100.0
        p_ci = 1.96 * math.sqrt((p_defect_rate / 100.0) * (1 - p_defect_rate / 100.0) / N) * 100.0

        b_waste_mean = float(np.mean(b_wastes))
        p_waste_mean = float(np.mean(p_wastes))
        waste_reduction = float(((b_waste_mean - p_waste_mean) / b_waste_mean) * 100.0)

        benchmark_results.append({
            "sample_size": N,
            "baseline": {
                "avg_setup_time_mins": round(b_time_mean, 2),
                "setup_time_std": round(b_time_std, 2),
                "defect_rate_pct": round(b_defect_rate, 2),
                "defect_rate_ci_95": round(b_ci, 2),
                "avg_waste_kg": round(b_waste_mean, 2)
            },
            "prototype": {
                "avg_setup_time_mins": round(p_time_mean, 2),
                "setup_time_std": round(p_time_std, 2),
                "defect_rate_pct": round(p_defect_rate, 2),
                "defect_rate_ci_95": round(p_ci, 2),
                "avg_waste_kg": round(p_waste_mean, 2)
            },
            "improvements": {
                "setup_time_improvement_pct": round(time_improvement, 2),
                "defect_rate_reduction_pct": round(defect_reduction, 2),
                "waste_reduction_pct": round(waste_reduction, 2)
            }
        })

    report = {
        "disclaimer": SAFETY_DISCLAIMER,
        "benchmark_runs": benchmark_results
    }

    # Save benchmark json report
    out_dir = os.path.dirname(__file__)
    json_path = os.path.join(out_dir, "benchmark_report.json")
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)

    return report

def print_benchmark_table(report: Dict[str, Any]):
    print("\n==========================================================================")
    print("      QUANTIFIED SIMULATION BENCHMARK REPORT (Baseline vs Prototype)")
    print("==========================================================================\n")
    print(f"{'Run N':<8} {'Metric':<25} {'Baseline':<20} {'Prototype':<20} {'Improvement':<12}")
    print("-" * 88)
    
    for run in report["benchmark_runs"]:
        N = run["sample_size"]
        b = run["baseline"]
        p = run["prototype"]
        imp = run["improvements"]

        b_t_str = f"{b['avg_setup_time_mins']:.2f} +/- {b['setup_time_std']:.2f}"
        p_t_str = f"{p['avg_setup_time_mins']:.2f} +/- {p['setup_time_std']:.2f}"
        b_d_str = f"{b['defect_rate_pct']:.2f}% +/- {b['defect_rate_ci_95']:.2f}%"
        p_d_str = f"{p['defect_rate_pct']:.2f}% +/- {p['defect_rate_ci_95']:.2f}%"

        print(f"{N:<8} {'Setup Time (min)':<25} {b_t_str:<20} {p_t_str:<20} {imp['setup_time_improvement_pct']:.2f}%")
        print(f"{'':<8} {'Defect Rate (95% CI)':<25} {b_d_str:<20} {p_d_str:<20} {imp['defect_rate_reduction_pct']:.2f}%")
        print(f"{'':<8} {'Material Waste (kg)':<25} {b['avg_waste_kg']:.2f} kg             {p['avg_waste_kg']:.2f} kg             {imp['waste_reduction_pct']:.2f}%")
        print("-" * 88)

if __name__ == "__main__":
    rep = run_simulation_benchmark()
    print_benchmark_table(rep)
