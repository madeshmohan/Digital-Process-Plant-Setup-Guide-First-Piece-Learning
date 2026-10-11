import pytest
import os
from analytics.benchmark import run_simulation_benchmark

def test_simulation_benchmark_generation():
    report = run_simulation_benchmark(sample_sizes=[50, 100])
    assert "disclaimer" in report
    assert "benchmark_runs" in report
    assert len(report["benchmark_runs"]) == 2

    run_50 = report["benchmark_runs"][0]
    assert run_50["sample_size"] == 50
    assert "baseline" in run_50
    assert "prototype" in run_50
    assert "improvements" in run_50

    # Baseline setup time should be greater than prototype setup time
    assert run_50["baseline"]["avg_setup_time_mins"] > run_50["prototype"]["avg_setup_time_mins"]
    # Baseline defect rate should be greater than prototype defect rate
    assert run_50["baseline"]["defect_rate_pct"] > run_50["prototype"]["defect_rate_pct"]
    assert run_50["improvements"]["setup_time_improvement_pct"] > 0
    assert run_50["improvements"]["defect_rate_reduction_pct"] > 0

    # Verify JSON file generated
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "analytics", "benchmark_report.json")
    assert os.path.exists(json_path)
