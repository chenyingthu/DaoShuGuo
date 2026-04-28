from e2e_utils import (
    baseline_phase_outputs,
    generate_e2e_report,
    harness_phase_outputs,
    quality_for_outputs,
)


def test_baseline_quality_without_harness():
    metrics = quality_for_outputs(baseline_phase_outputs())

    assert metrics["average_score"] < 60
    assert metrics["required_coverage"] < 60
    assert metrics["total_missing_fields"] > 0


def test_harness_quality_improvement():
    metrics = quality_for_outputs(harness_phase_outputs())

    assert metrics["average_score"] >= 80
    assert metrics["required_coverage"] == 100.0
    assert metrics["total_missing_fields"] == 0


def test_quality_improvement_significant(tmp_path):
    baseline = quality_for_outputs(baseline_phase_outputs())
    experiment = quality_for_outputs(harness_phase_outputs())
    improvement = ((experiment["average_score"] - baseline["average_score"]) / baseline["average_score"]) * 100

    assert improvement > 50
    assert experiment["required_coverage"] == 100.0

    report = generate_e2e_report(tmp_path / "E2E_TEST_REPORT.yaml", baseline, experiment)
    assert report["test_summary"]["score_improvement_percent"] > 50
    assert (tmp_path / "E2E_TEST_REPORT.yaml").exists()
