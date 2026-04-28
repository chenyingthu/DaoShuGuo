#!/usr/bin/env python3
"""
Research Quality Verification Tool

验证研究记录是否符合质量标准，基于 schemas/ 和 configs/phase_requirements.yaml

Usage:
    python3 scripts/verify_research_quality.py --run-dir runs/task003/run_001 --output report.yaml
    python3 scripts/verify_research_quality.py --input work_brief.yaml --phase skill_execution

Exit codes:
    0 - All checks passed
    1 - Some checks failed
    2 - Critical errors (file not found, etc.)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import yaml

# 添加项目路径
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agents.validation_agent import ValidationAgent, ValidationResult


@dataclass
class QualityReport:
    """质量验证报告"""
    run_dir: Path
    overall_score: float = 0.0
    overall_status: str = "pending"  # passed, failed, partial
    phases_checked: int = 0
    phases_passed: int = 0
    phases_failed: int = 0
    total_missing_fields: int = 0
    total_shallow_fields: int = 0
    total_warnings: int = 0
    phase_results: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


def find_phase_outputs(run_dir: Path) -> Dict[str, Path]:
    """
    在运行目录中查找所有 phase 输出文件

    Returns:
        Dict[phase_name, file_path]
    """
    phase_files = {}

    # 检查常见的 phase 输出位置
    phase_names = [
        "skill_change_request",
        "skill_execution",
        "effectiveness_assessment",
        "cognition_diagnosis",
        "work_brief",
        "execution_record",
        "assessment_packet",
    ]

    # 检查根目录
    for name in phase_names:
        for ext in [".yaml", ".yml", ".json"]:
            file_path = run_dir / f"{name}{ext}"
            if file_path.exists():
                phase_files[name] = file_path
                break

    # 检查 phase_transitions 目录
    transitions_dir = run_dir / "phase_transitions"
    if transitions_dir.exists():
        for file_path in transitions_dir.glob("*.yaml"):
            # 从文件名提取 phase 名 (如 "01_skill_change_request.yaml")
            name = file_path.stem.split("_", 1)[1] if "_" in file_path.stem else file_path.stem
            if name not in phase_files:
                phase_files[name] = file_path

    # 检查 review 目录
    review_dir = run_dir / "review"
    if review_dir.exists():
        for file_path in review_dir.glob("*.yaml"):
            name = file_path.stem
            if name not in phase_files:
                phase_files[name] = file_path

    return phase_files


def calculate_quality_score(result: ValidationResult) -> float:
    """
    计算质量分数

    基于:
    - 必填字段完整度
    - 内容深度
    - 警告数量
    """
    score = 100.0

    # 缺失字段扣分 (每个 -10分)
    score -= len(result.missing_fields) * 10

    # 简略字段扣分 (每个 -5分)
    score -= len(result.shallow_fields) * 5

    # 错误扣分 (每个 -15分)
    score -= len(result.content_errors) * 15

    # 警告扣分 (每个 -2分)
    score -= len(result.warnings) * 2

    # 内容长度加分
    if result.min_required_length > 0:
        length_ratio = min(result.content_length / result.min_required_length, 2.0)
        score += (length_ratio - 1.0) * 10  # 超长内容加分

    return max(0.0, min(100.0, score))


def generate_recommendations(results: List[ValidationResult]) -> List[str]:
    """生成改进建议"""
    recommendations = []

    # 统计常见问题
    all_missing = set()
    all_shallow = set()

    for result in results:
        all_missing.update(result.missing_fields)
        all_shallow.update(result.shallow_fields)

    # 基于常见问题生成建议
    if "failure_capsule.known_limitations" in all_missing or "failure_capsule.known_limitations" in all_shallow:
        recommendations.append(
            "建议: 始终记录 failure_capsule.known_limitations，即使研究'成功'也要记录局限性"
        )

    if "skill_implementation.code.structure" in all_missing:
        recommendations.append(
            "建议: 添加 skill_implementation.code.structure，描述核心函数和算法"
        )

    if "hypothesis.testable_prediction" in all_missing:
        recommendations.append(
            "建议: hypothesis.testable_prediction 必须包含可量化指标（如 >5%）"
        )

    if any("method.description" in r.missing_fields for r in results):
        recommendations.append(
            "建议: method.description 必须详细描述方法，至少100字符"
        )

    if not recommendations:
        recommendations.append("所有基本字段已满足，建议进一步丰富内容和细节")

    return recommendations


def verify_run_directory(run_dir: Path, strict: bool = False) -> QualityReport:
    """
    验证整个运行目录

    Args:
        run_dir: 运行目录路径
        strict: 严格模式（任何错误都算失败）

    Returns:
        QualityReport: 质量报告
    """
    print(f"\n{'='*70}")
    print(f"Research Quality Verification")
    print(f"Run Directory: {run_dir}")
    print(f"{'='*70}\n")

    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    # 初始化 Validation Agent
    agent = ValidationAgent(
        schema_dir=str(REPO_ROOT / "schemas"),
        config_path=str(REPO_ROOT / "configs" / "phase_requirements.yaml")
    )

    # 查找 phase 输出文件
    phase_files = find_phase_outputs(run_dir)

    if not phase_files:
        print("Warning: No phase output files found in run directory")
        return QualityReport(
            run_dir=run_dir,
            overall_status="failed",
            recommendations=["No phase output files found. Ensure the run completed successfully."]
        )

    print(f"Found {len(phase_files)} phase output files:")
    for phase, path in phase_files.items():
        print(f"  - {phase}: {path.name}")

    # 验证每个 phase
    report = QualityReport(run_dir=run_dir)
    validation_results = []

    for phase_name, file_path in sorted(phase_files.items()):
        print(f"\n{'-'*70}")
        print(f"Checking phase: {phase_name}")
        print(f"File: {file_path}")
        print(f"{'-'*70}")

        # 确定该文件对应的 phase 类型
        phase_type = phase_name
        if phase_name not in agent.phase_requirements:
            # 尝试映射到标准 phase
            phase_mapping = {
                "work_brief": "skill_execution",
                "execution_record": "skill_execution",
                "assessment_packet": "effectiveness_assessment",
            }
            phase_type = phase_mapping.get(phase_name, phase_name)

        if phase_type not in agent.phase_requirements:
            print(f"  ⚠️  No requirements found for phase '{phase_type}', skipping validation")
            continue

        # 执行验证
        result = agent.validate_from_file(str(file_path), phase_type)
        validation_results.append(result)

        # 计算分数
        score = calculate_quality_score(result)

        # 更新报告
        report.phases_checked += 1
        if result.valid:
            report.phases_passed += 1
            status = "passed"
        else:
            report.phases_failed += 1
            status = "failed"

        report.total_missing_fields += len(result.missing_fields)
        report.total_shallow_fields += len(result.shallow_fields)
        report.total_warnings += len(result.warnings)

        # 记录 phase 结果
        phase_report = {
            "phase": phase_name,
            "file": str(file_path.relative_to(run_dir)),
            "status": status,
            "score": round(score, 1),
            "valid": result.valid,
            "missing_fields": result.missing_fields,
            "shallow_fields": result.shallow_fields,
            "errors": result.content_errors,
            "warnings": result.warnings,
            "content_length": result.content_length,
            "min_required_length": result.min_required_length,
        }
        report.phase_results.append(phase_report)

        # 打印结果
        print(f"  Score: {score:.1f}/100")
        print(f"  Status: {status}")
        print(f"  Missing fields: {len(result.missing_fields)}")
        print(f"  Shallow fields: {len(result.shallow_fields)}")
        print(f"  Errors: {len(result.content_errors)}")
        print(f"  Warnings: {len(result.warnings)}")
        print(f"  Content length: {result.content_length} chars")

        if not result.valid:
            print(f"\n  Feedback preview:")
            feedback_lines = result.feedback.split('\n')[:10]
            for line in feedback_lines:
                print(f"    {line}")

    # 计算总体分数
    if report.phases_checked > 0:
        scores = [calculate_quality_score(r) for r in validation_results]
        report.overall_score = round(sum(scores) / len(scores), 1)

        # 确定总体状态
        if report.phases_failed == 0:
            report.overall_status = "passed"
        elif report.phases_passed == 0:
            report.overall_status = "failed"
        else:
            report.overall_status = "partial"
    else:
        report.overall_status = "failed"

    # 生成建议
    report.recommendations = generate_recommendations(validation_results)

    return report


def format_report(report: QualityReport, format_type: str = "yaml") -> str:
    """格式化报告输出"""
    if format_type == "yaml":
        output = {
            "schema_version": "0.1.0",
            "object_type": "quality_report",
            "run_dir": str(report.run_dir),
            "overall": {
                "score": report.overall_score,
                "status": report.overall_status,
                "phases_checked": report.phases_checked,
                "phases_passed": report.phases_passed,
                "phases_failed": report.phases_failed,
            },
            "summary": {
                "total_missing_fields": report.total_missing_fields,
                "total_shallow_fields": report.total_shallow_fields,
                "total_warnings": report.total_warnings,
            },
            "phase_results": report.phase_results,
            "recommendations": report.recommendations,
        }
        return yaml.dump(output, default_flow_style=False, allow_unicode=True)

    elif format_type == "json":
        output = {
            "schema_version": "0.1.0",
            "object_type": "quality_report",
            "run_dir": str(report.run_dir),
            "overall": {
                "score": report.overall_score,
                "status": report.overall_status,
                "phases_checked": report.phases_checked,
                "phases_passed": report.phases_passed,
                "phases_failed": report.phases_failed,
            },
            "summary": {
                "total_missing_fields": report.total_missing_fields,
                "total_shallow_fields": report.total_shallow_fields,
                "total_warnings": report.total_warnings,
            },
            "phase_results": report.phase_results,
            "recommendations": report.recommendations,
        }
        return json.dumps(output, indent=2, ensure_ascii=False)

    elif format_type == "markdown":
        lines = [
            "# Research Quality Report",
            "",
            f"**Run Directory:** `{report.run_dir}`",
            f"**Overall Score:** {report.overall_score:.1f}/100",
            f"**Status:** {report.overall_status.upper()}",
            "",
            "## Summary",
            "",
            f"- Phases checked: {report.phases_checked}",
            f"- Phases passed: {report.phases_passed}",
            f"- Phases failed: {report.phases_failed}",
            f"- Total missing fields: {report.total_missing_fields}",
            f"- Total shallow fields: {report.total_shallow_fields}",
            f"- Total warnings: {report.total_warnings}",
            "",
            "## Phase Results",
            "",
        ]

        for phase in report.phase_results:
            status_emoji = "✅" if phase["status"] == "passed" else "❌"
            lines.append(f"### {phase['phase']} {status_emoji}")
            lines.append("")
            lines.append(f"- **File:** `{phase['file']}`")
            lines.append(f"- **Score:** {phase['score']}/100")
            lines.append(f"- **Missing fields:** {len(phase['missing_fields'])}")
            lines.append(f"- **Shallow fields:** {len(phase['shallow_fields'])}")
            lines.append(f"- **Errors:** {len(phase['errors'])}")
            lines.append(f"- **Warnings:** {len(phase['warnings'])}")
            lines.append("")

        lines.append("## Recommendations")
        lines.append("")
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

        return "\n".join(lines)

    else:
        raise ValueError(f"Unknown format type: {format_type}")


def main():
    parser = argparse.ArgumentParser(
        description="Verify research record quality against standards"
    )
    parser.add_argument(
        "--run-dir", "-r",
        type=Path,
        help="Run directory to verify"
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        help="Single input file to verify (alternative to --run-dir)"
    )
    parser.add_argument(
        "--phase", "-p",
        help="Phase type for single file verification"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["yaml", "json", "markdown"],
        default="yaml",
        help="Output format (default: yaml)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: any error counts as failure"
    )
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=70.0,
        help="Minimum score threshold (default: 70.0)"
    )

    args = parser.parse_args()

    try:
        # 验证输入
        if args.run_dir:
            report = verify_run_directory(args.run_dir, strict=args.strict)
        elif args.input and args.phase:
            # 单文件验证模式
            agent = ValidationAgent()
            result = agent.validate_from_file(str(args.input), args.phase)
            score = calculate_quality_score(result)

            report = QualityReport(run_dir=args.input.parent)
            report.phases_checked = 1
            report.phases_passed = 1 if result.valid else 0
            report.phases_failed = 0 if result.valid else 1
            report.total_missing_fields = len(result.missing_fields)
            report.total_shallow_fields = len(result.shallow_fields)
            report.total_warnings = len(result.warnings)
            report.overall_score = score
            report.overall_status = "passed" if result.valid else "failed"
            report.phase_results = [{
                "phase": args.phase,
                "file": str(args.input),
                "status": "passed" if result.valid else "failed",
                "score": round(score, 1),
                "valid": result.valid,
                "missing_fields": result.missing_fields,
                "shallow_fields": result.shallow_fields,
                "errors": result.content_errors,
                "warnings": result.warnings,
            }]
            report.recommendations = generate_recommendations([result])
        else:
            parser.error("Either --run-dir or both --input and --phase must be specified")

        # 格式化输出
        output = format_report(report, args.format)

        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"\nReport written to: {args.output}")
        else:
            print("\n" + "="*70)
            print("Verification Report")
            print("="*70)
            print(output)

        # 打印摘要
        print("\n" + "="*70)
        print("Summary")
        print("="*70)
        print(f"Overall Score: {report.overall_score:.1f}/100")
        print(f"Status: {report.overall_status.upper()}")
        print(f"Phases: {report.phases_passed}/{report.phases_checked} passed")

        if report.recommendations:
            print("\nTop Recommendations:")
            for i, rec in enumerate(report.recommendations[:3], 1):
                print(f"  {i}. {rec}")

        # 根据结果返回退出码
        if report.overall_status == "passed":
            if report.overall_score >= args.score_threshold:
                return 0
            else:
                print(f"\nWarning: Score {report.overall_score:.1f} below threshold {args.score_threshold}")
                return 1
        else:
            return 1

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
