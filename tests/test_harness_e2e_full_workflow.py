from e2e_utils import calculate_quality_metrics, generate_e2e_report, run_engine_with_harness


def test_complete_workflow_with_harness():
    run_dir = run_engine_with_harness(run_name="pytest_full_workflow")
    metrics = calculate_quality_metrics(run_dir)

    assert metrics["average_score"] >= 80
    assert metrics["required_coverage"] == 100.0
    assert metrics["total_missing_fields"] == 0
    assert (run_dir / "artifact_index.json").exists()


def test_generate_e2e_report(tmp_path):
    baseline = {
        "average_score": 40.0,
        "required_coverage": 35.0,
        "total_missing_fields": 10,
        "total_shallow_fields": 2,
        "total_content_errors": 5,
        "phase_results": [],
    }
    experiment = {
        "average_score": 90.0,
        "required_coverage": 100.0,
        "total_missing_fields": 0,
        "total_shallow_fields": 0,
        "total_content_errors": 0,
        "phase_results": [],
    }

    report = generate_e2e_report(tmp_path / "report.md", baseline, experiment)

    assert report["test_summary"]["score_improvement_percent"] == 125.0
    assert "improves" in report["conclusion"]
    assert (tmp_path / "report.md").exists()
