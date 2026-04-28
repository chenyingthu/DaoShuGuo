#!/usr/bin/env python3
"""
Harness End-to-End Integration Test

真实端到端测试：使用真实 task adapter 运行完整 workflow
验证改进后的引擎是否能产生符合质量标准的输出

Usage:
    python3 tests/test_harness_e2e.py --task task007_fixture --verbose
    python3 tests/test_harness_e2e.py --task task003 --backend deterministic
"""

import argparse
import os
import shutil
import sys
import tempfile
import time
import yaml
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agents.validation_agent import ValidationAgent


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'


def print_header(text):
    print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")


def print_section(text):
    print(f"\n{Colors.BLUE}{'-'*70}{Colors.RESET}")
    print(f"{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'-'*70}{Colors.RESET}\n")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    print(f"  {text}")


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


class EndToEndTest:
    """端到端测试类"""

    def __init__(self, task_id, backend="deterministic", verbose=False, keep_workspace=False):
        self.task_id = task_id
        self.backend = backend
        self.verbose = verbose
        self.keep_workspace = keep_workspace
        self.workspace_root = None
        self.test_results = []
        self.validation_agent = None

        # 路径
        self.adapter_path = REPO_ROOT / "adapters" / f"{task_id}.yaml"
        self.task_path = REPO_ROOT / "tasks" / task_id

    def setup(self):
        """测试准备"""
        print_header(f"End-to-End Test Setup")
        print(f"Task: {self.task_id}")
        print(f"Backend: {self.backend}")
        print(f"Time: {datetime.now().isoformat()}")

        # 检查必要文件
        if not self.adapter_path.exists():
            print_error(f"Adapter not found: {self.adapter_path}")
            return False
        print_success(f"Adapter found: {self.adapter_path}")

        # 加载 adapter
        self.adapter = load_yaml(self.adapter_path)
        print_info(f"Task ref: {self.adapter['task_ref']}")

        # 创建工作目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.workspace_root = REPO_ROOT / "runs" / self.task_id / f"harness_e2e_{timestamp}"
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        print_success(f"Workspace created: {self.workspace_root}")

        # 初始化 Validation Agent
        self.validation_agent = ValidationAgent(
            schema_dir=str(REPO_ROOT / "schemas"),
            config_path=str(REPO_ROOT / "configs" / "phase_requirements.yaml")
        )
        print_success("Validation Agent initialized")

        return True

    def run_harness_engine(self):
        """运行 Harness 引擎"""
        print_section("Running Harness Engine")

        try:
            # 导入引擎
            sys.path.insert(0, str(REPO_ROOT / "scripts"))
            from run_generic_loop_engine_with_harness import GenericLoopEngineWithHarness

            # 配置
            loop_config = {
                "phases": [
                    "skill_change_request",
                    "skill_execution",
                    "effectiveness_assessment",
                    "cognition_diagnosis",
                    "loop_routing_decision",
                ]
            }

            # 确定 worker 模块路径
            task_workers = REPO_ROOT / f"scripts/generic_loop_engine_{self.task_id}_workers.py"
            fixture_workers = REPO_ROOT / "scripts/generic_loop_engine_fixture_workers.py"

            if task_workers.exists():
                worker_module = str(task_workers.relative_to(REPO_ROOT))
            else:
                worker_module = str(fixture_workers.relative_to(REPO_ROOT))

            backend_config = {
                "backend_id": self.backend,
                "worker_module": worker_module,
            }

            print_info(f"Using worker module: {backend_config['worker_module']}")

            # 创建引擎
            engine = GenericLoopEngineWithHarness(
                task_adapter_path=self.adapter_path,
                workspace_root=self.workspace_root,
                run_intent=f"E2E test with harness for {self.task_id}",
                loop_config=loop_config,
                verifier_config={},
                backend=self.backend,
                backend_config=backend_config,
                validation_enabled=True,
                strict_mode=False,  # 非严格模式，允许记录失败
            )

            # 运行
            print_info("Starting engine run...")
            start_time = time.time()
            result_path = engine.run()
            elapsed = time.time() - start_time

            print_success(f"Engine completed in {elapsed:.1f}s")
            print_info(f"Output: {result_path}")

            return True, result_path

        except Exception as e:
            print_error(f"Engine failed: {e}")
            import traceback
            traceback.print_exc()
            return False, None

    def analyze_outputs(self):
        """分析生成的输出文件"""
        print_section("Analyzing Generated Outputs")

        # 查找所有生成的文件
        phase_transitions_dir = self.workspace_root / "phase_transitions"
        artifacts_dir = self.workspace_root / "artifacts"

        if not phase_transitions_dir.exists():
            print_error("No phase transitions directory found")
            return False

        # 列出所有 phase 文件
        phase_files = sorted(phase_transitions_dir.glob("*.yaml"))
        print_info(f"Found {len(phase_files)} phase transition files:")

        for pf in phase_files:
            print_info(f"  - {pf.name}")

        # 验证每个 phase 的输出
        validation_results = []

        phase_mapping = {
            "01_skill_change_request": ("skill_change_request", "work_brief"),
            "02_skill_execution": ("skill_execution", "execution_record"),
            "03_effectiveness_assessment": ("effectiveness_assessment", "assessment_packet"),
            "04_cognition_diagnosis": ("cognition_diagnosis", "cognition_diagnosis"),
            "05_loop_routing_decision": ("loop_routing_decision", "routing_decision"),
        }

        for phase_file in phase_files:
            phase_key = phase_file.stem
            if phase_key in phase_mapping:
                phase_name, expected_type = phase_mapping[phase_key]
                print_section(f"Validating {phase_name}")

                # 加载 phase transition 文件
                transition_data = load_yaml(phase_file)
                status = transition_data.get("status", "unknown")
                output_ref = transition_data.get("output_ref")

                print_info(f"Status: {status}")
                print_info(f"Output ref: {output_ref}")

                # 查找对应的 artifact 文件
                artifact_file = None
                if artifacts_dir.exists():
                    for af in artifacts_dir.rglob("*.yaml"):
                        if output_ref and output_ref in str(af):
                            artifact_file = af
                            break

                if artifact_file:
                    print_info(f"Artifact: {artifact_file.relative_to(self.workspace_root)}")

                    # 验证 artifact
                    result = self.validation_agent.validate_from_file(
                        str(artifact_file),
                        phase_name
                    )

                    validation_results.append({
                        "phase": phase_name,
                        "valid": result.valid,
                        "score": self._calculate_score(result),
                        "missing": len(result.missing_fields),
                        "shallow": len(result.shallow_fields),
                        "errors": len(result.content_errors),
                        "warnings": len(result.warnings),
                        "content_length": result.content_length,
                    })

                    if result.valid:
                        print_success(f"Validation passed")
                    else:
                        print_warning(f"Validation issues found")

                    print_info(f"  Content length: {result.content_length}")
                    print_info(f"  Missing fields: {len(result.missing_fields)}")
                    print_info(f"  Shallow fields: {len(result.shallow_fields)}")

                    if self.verbose and not result.valid:
                        print_info(f"\nFeedback preview:")
                        for line in result.feedback.split('\n')[:15]:
                            print_info(f"    {line}")
                else:
                    print_warning(f"Artifact file not found for {output_ref}")
                    validation_results.append({
                        "phase": phase_name,
                        "valid": False,
                        "score": 0,
                        "missing": 0,
                        "shallow": 0,
                        "errors": 1,
                        "warnings": 0,
                        "content_length": 0,
                    })

        # 保存验证结果
        self.validation_results = validation_results
        return True

    def _calculate_score(self, result):
        """计算质量分数"""
        score = 100.0
        score -= len(result.missing_fields) * 10
        score -= len(result.shallow_fields) * 5
        score -= len(result.content_errors) * 15
        score -= len(result.warnings) * 2
        return max(0, min(100, score))

    def generate_report(self):
        """生成测试报告"""
        print_section("Test Report")

        if not hasattr(self, 'validation_results'):
            print_error("No validation results available")
            return

        total_phases = len(self.validation_results)
        passed_phases = sum(1 for r in self.validation_results if r['valid'])
        avg_score = sum(r['score'] for r in self.validation_results) / total_phases if total_phases > 0 else 0

        print(f"\n{Colors.BLUE}Summary:{Colors.RESET}")
        print_info(f"Total phases: {total_phases}")
        print_info(f"Passed: {passed_phases}")
        print_info(f"Failed: {total_phases - passed_phases}")
        print_info(f"Average score: {avg_score:.1f}/100")

        print(f"\n{Colors.BLUE}Phase Details:{Colors.RESET}")
        for result in self.validation_results:
            status = f"{Colors.GREEN}✓{Colors.RESET}" if result['valid'] else f"{Colors.RED}✗{Colors.RESET}"
            print_info(f"{status} {result['phase']}: {result['score']:.1f} "
                      f"(missing:{result['missing']}, shallow:{result['shallow']})")

        # 保存报告到文件
        report_path = self.workspace_root / "e2e_test_report.yaml"
        report = {
            "test_info": {
                "task_id": self.task_id,
                "backend": self.backend,
                "timestamp": datetime.now().isoformat(),
                "workspace": str(self.workspace_root),
            },
            "summary": {
                "total_phases": total_phases,
                "passed": passed_phases,
                "failed": total_phases - passed_phases,
                "average_score": round(avg_score, 1),
                "overall_status": "passed" if passed_phases == total_phases else "partial" if passed_phases > 0 else "failed"
            },
            "phase_results": self.validation_results
        }

        with open(report_path, 'w') as f:
            yaml.dump(report, f, default_flow_style=False, allow_unicode=True)

        print_success(f"Report saved: {report_path}")

        return avg_score, passed_phases, total_phases

    def compare_with_baseline(self):
        """与基线（无 harness）对比"""
        print_section("Comparison with Baseline (No Harness)")

        # 检查典型问题
        issues_found = []

        for result in self.validation_results:
            if result['shallow'] > 0:
                issues_found.append(f"{result['phase']}: {result['shallow']} shallow fields")
            if result['missing'] > 0:
                issues_found.append(f"{result['phase']}: {result['missing']} missing fields")

        if issues_found:
            print_warning("Issues that would be missed without harness:")
            for issue in issues_found:
                print_info(f"  - {issue}")
        else:
            print_success("No major quality issues detected")

    def cleanup(self):
        """清理"""
        if self.keep_workspace:
            print_section(f"Workspace preserved: {self.workspace_root}")
        else:
            print_section("Cleaning up")
            if self.workspace_root and self.workspace_root.exists():
                shutil.rmtree(self.workspace_root, ignore_errors=True)
                print_info(f"Removed: {self.workspace_root}")

    def run(self):
        """运行完整测试"""
        print_header(f"Harness E2E Test: {self.task_id}")

        # 准备
        if not self.setup():
            return 1

        try:
            # 运行引擎
            success, result_path = self.run_harness_engine()
            if not success:
                return 1

            # 分析输出
            if not self.analyze_outputs():
                return 1

            # 生成报告
            avg_score, passed, total = self.generate_report()

            # 对比分析
            self.compare_with_baseline()

            # 最终结论
            print_header("Final Result")
            if passed == total:
                print_success(f"All {total} phases passed validation!")
                print_info(f"Average quality score: {avg_score:.1f}/100")
                return 0
            elif passed > 0:
                print_warning(f"Partial success: {passed}/{total} phases passed")
                print_info(f"Average quality score: {avg_score:.1f}/100")
                print_info("Some phases need improvement")
                return 1
            else:
                print_error(f"All phases failed validation")
                return 2

        finally:
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description="Run end-to-end test with harness"
    )
    parser.add_argument(
        "--task", "-t",
        default="task007_fixture",
        help="Task ID to test (default: task007_fixture)"
    )
    parser.add_argument(
        "--backend", "-b",
        default="deterministic",
        help="Backend to use (default: deterministic)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--keep-workspace", "-k",
        action="store_true",
        help="Keep workspace after test"
    )

    args = parser.parse_args()

    test = EndToEndTest(
        task_id=args.task,
        backend=args.backend,
        verbose=args.verbose,
        keep_workspace=args.keep_workspace
    )

    return test.run()


if __name__ == "__main__":
    sys.exit(main())
