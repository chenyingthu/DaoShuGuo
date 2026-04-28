from pathlib import Path

from e2e_utils import load_yaml, validate_phase_payload, validation_agent


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"


def test_missing_required_fields():
    payload = load_yaml(FIXTURE_ROOT / "low_quality" / "work_brief_incomplete.yaml")
    result = validate_phase_payload(payload, "skill_change_request")

    assert result.valid is False
    assert "hypothesis.rationale" in result.missing_fields
    assert "method.description" in result.missing_fields
    assert "method.description" in result.feedback


def test_shallow_content():
    payload = load_yaml(FIXTURE_ROOT / "low_quality" / "work_brief_shallow.yaml")
    result = validate_phase_payload(payload, "skill_change_request")

    assert result.valid is False
    assert "hypothesis.statement" in result.shallow_fields
    assert "method.description" in result.shallow_fields
    assert "内容过于简略" in result.feedback


def test_valid_output():
    payload = load_yaml(FIXTURE_ROOT / "high_quality" / "work_brief_complete.yaml")
    result = validate_phase_payload(payload, "skill_change_request")

    assert result.valid is True
    assert result.missing_fields == []
    assert result.shallow_fields == []


def test_fixture_dataset_covers_quality_edges():
    agent = validation_agent()
    low_quality = sorted((FIXTURE_ROOT / "low_quality").glob("*.yaml"))
    high_quality = sorted((FIXTURE_ROOT / "high_quality").glob("*.yaml"))

    assert len(low_quality) >= 3
    assert len(high_quality) >= 3

    assert any(not agent.validate_from_file(str(path), "skill_change_request").valid for path in low_quality)
    assert agent.validate_from_file(
        str(FIXTURE_ROOT / "high_quality" / "execution_record_complete.yaml"),
        "skill_execution",
    ).valid
    assert agent.validate_from_file(
        str(FIXTURE_ROOT / "high_quality" / "assessment_packet_complete.yaml"),
        "effectiveness_assessment",
    ).valid
