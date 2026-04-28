#!/usr/bin/env python3
"""
Harness Integration Tests

集成测试 Generic Loop Engine with Validation Harness

Usage:
    python3 tests/test_harness_integration.py
    python3 tests/test_harness_integration.py --verbose
"""

import argparse
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目路径
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import yaml
from agents.validation_agent import ValidationAgent, ValidationResult


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_success(text):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    """打印信息"""
    print(f"  {text}")


class HarnessIntegrationTest:
    """Harness 集成测试类"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.test_results = []
        self.agent = None

    def setup(self):
        """测试前置准备"""
        print_header("Test Setup")

        # 初始化 Validation Agent
        try:
            self.agent = ValidationAgent(
                schema_dir=str(REPO_ROOT / "schemas"),
                config_path=str(REPO_ROOT / "configs" / "phase_requirements.yaml")
            )
            print_success("Validation Agent initialized")
            print_info(f"Loaded {len(self.agent.schemas)} schemas")
            print_info(f"Loaded {len(self.agent.phase_requirements)} phase requirements")
        except Exception as e:
            print_error(f"Failed to initialize Validation Agent: {e}")
            return False

        return True

    def teardown(self):
        """测试后置清理"""
        print_header("Test Teardown")
        print_info("Cleaning up temporary files...")
        # 清理工作已在各测试中完成

    def record_result(self, test_name, passed, details=None):
        """记录测试结果"""
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "details": details
        })
        return passed

    # =================================================================
    # Test 1: Schema Loading
    # =================================================================
    def test_schema_loading(self):
        """测试 Schema 加载"""
        print_header("Test 1: Schema Loading")

        required_schemas = [
            "work_brief",
            "execution_record",
            "assessment_packet",
            "skill_implementation"
        ]

        all_loaded = True
        for schema_name in required_schemas:
            if schema_name in self.agent.schemas:
                print_success(f"Schema loaded: {schema_name}")
            else:
                print_error(f"Schema missing: {schema_name}")
                all_loaded = False

        return self.record_result("Schema Loading", all_loaded)

    # =================================================================
    # Test 2: Phase Requirements Loading
    # =================================================================
    def test_phase_requirements_loading(self):
        """测试 Phase 配置加载"""
        print_header("Test 2: Phase Requirements Loading")

        required_phases = [
            "skill_change_request",
            "skill_execution",
            "effectiveness_assessment",
            "cognition_diagnosis"
        ]

        all_loaded = True
        for phase_name in required_phases:
            if phase_name in self.agent.phase_requirements:
                req = self.agent.phase_requirements[phase_name]
                must_include = req.get("must_include", [])
                print_success(f"Phase loaded: {phase_name} ({len(must_include)} required fields)")
                if self.verbose:
                    for field in must_include[:3]:
                        print_info(f"  - {field}")
            else:
                print_error(f"Phase missing: {phase_name}")
                all_loaded = False

        return self.record_result("Phase Requirements Loading", all_loaded)

    # =================================================================
    # Test 3: Valid Output Validation
    # =================================================================
    def test_valid_output_validation(self):
        """测试有效输出验证"""
        print_header("Test 3: Valid Output Validation")

        # 创建一个符合要求的输出
        valid_output = {
            "schema_version": "0.1.0",
            "object_type": "work_brief",
            "phase": "skill_execution",
            "hypothesis": {
                "statement": "在IEEE69网络的高电压偏差节点添加无功补偿，可以降低网损并改善电压分布",
                "rationale": "基于无功功率-电压耦合关系，Q注入可减少线路无功传输",
                "testable_prediction": "补偿后网损降低>5%，电压偏差改善>10%"
            },
            "method": {
                "name": "weak_node_reactive_compensation",
                "description": "识别电压最低的三个节点，添加并联电容器进行无功补偿。使用贪心算法逐步增加补偿量直到满足约束条件。",
                "algorithm": {
                    "type": "greedy_local_search",
                    "steps": [
                        "计算所有节点的电压幅值",
                        "识别V < 0.95 p.u.的节点",
                        "在这些节点添加1.5 MVar并联电容",
                        "运行潮流计算",
                        "比较网损和电压指标"
                    ]
                },
                "code_location": "tasks/task003/candidate_solver.py:45-89"
            },
            "execution": {
                "status": "completed",
                "timestamp": "2026-04-27T10:30:00Z",
                "duration_seconds": 45,
                "inputs": {
                    "grid_model": "ieee69",
                    "base_load_mw": 3.8,
                    "simulator": "pandapower 2.14.0"
                },
                "outputs": {
                    "raw_result_path": "runs/task003/run_0021/artifacts/loadflow_result.json",
                    "metrics_path": "runs/task003/run_0021/artifacts/metrics.json"
                }
            },
            "skill_implementation": {
                "code": {
                    "main_file": "tasks/task003/candidate_solver.py",
                    "structure": [
                        {
                            "function": "identify_weak_nodes",
                            "purpose": "识别电压幅值最低的N个节点，用于后续补偿",
                            "algorithm": "排序 + 阈值筛选",
                            "complexity": "O(n log n)"
                        },
                        {
                            "function": "calculate_compensation",
                            "purpose": "根据电压偏差计算所需无功补偿量",
                            "algorithm": "线性插值",
                            "complexity": "O(n)"
                        }
                    ]
                },
                "design_decisions": [
                    {
                        "decision": "使用贪心算法而非全局优化",
                        "alternatives_considered": ["OPF", "遗传算法", "粒子群优化"],
                        "trade_offs": ["速度 vs 最优性：选择速度", "简单性 vs 精确性：选择简单性"],
                        "validated": True
                    }
                ]
            },
            "results": {
                "primary_metrics": {
                    "loss_before_mw": {
                        "value": 0.224,
                        "unit": "MW",
                        "context": "基线网损"
                    },
                    "loss_after_mw": {
                        "value": 0.198,
                        "unit": "MW",
                        "context": "补偿后网损"
                    },
                    "improvement_percent": {
                        "value": 11.6,
                        "unit": "%",
                        "is_significant": True,
                        "threshold_used": 5.0
                    }
                }
            },
            "failure_capsule": {
                "known_limitations": [
                    {
                        "limitation": "仅测试单工况(peak load)，无法评估负荷波动下的性能稳定性",
                        "impact": "无法保证方法鲁棒性",
                        "severity": "medium"
                    }
                ],
                "local_failures": [],
                "generalizability_gaps": [
                    "仅在IEEE69上测试",
                    "仅测试单一网络拓扑"
                ]
            },
            "next_actions": {
                "immediate": [
                    {
                        "action": "测试不同补偿位置组合",
                        "rationale": "当前固定位置可能非最优",
                        "expected_output": "位置敏感性分析报告"
                    }
                ],
                "short_term": [
                    {
                        "action": "引入文献方法进行对比",
                        "rationale": "需要基准判断方法先进性"
                    }
                ]
            }
        }

        result = self.agent.validate_phase_output(valid_output, "skill_execution")

        if self.verbose:
            print_info(f"Valid: {result.valid}")
            print_info(f"Missing fields: {result.missing_fields}")
            print_info(f"Shallow fields: {result.shallow_fields}")
            print_info(f"Errors: {result.content_errors}")
            print_info(f"Warnings: {result.warnings}")
            print_info(f"Content length: {result.content_length}")

        # 检查是否通过验证
        passed = result.valid

        if passed:
            print_success("Valid output passed validation")
        else:
            print_error("Valid output failed validation")
            if result.missing_fields:
                print_warning(f"Missing fields: {result.missing_fields}")

        return self.record_result("Valid Output Validation", passed)

    # =================================================================
    # Test 4: Invalid Output Detection
    # =================================================================
    def test_invalid_output_detection(self):
        """测试无效输出检测"""
        print_header("Test 4: Invalid Output Detection")

        # 创建一个不符合要求的输出（过于简略）
        invalid_output = {
            "schema_version": "0.1.0",
            "object_type": "work_brief",
            "phase": "skill_execution",
            "hypothesis": {
                "statement": "补偿可以降低损耗",  # ❌ 太短
                "testable_prediction": "变好"     # ❌ 无量化指标
            },
            "method": {
                "description": "使用算法优化",      # ❌ 太简略
                "algorithm": {
                    "type": "optimization"
                }
            },
            "skill_implementation": {
                "code": {
                    "main_file": "tasks/task003/solver.py",
                    "structure": []  # ❌ 为空
                }
            },
            "results": {
                "primary_metrics": {}  # ❌ 无指标
            },
            "failure_capsule": {
                "known_limitations": []  # ❌ 为空
            },
            "next_actions": {
                "immediate": []  # ❌ 为空
            }
        }

        result = self.agent.validate_phase_output(invalid_output, "skill_execution")

        if self.verbose:
            print_info(f"Valid: {result.valid}")
            print_info(f"Missing fields: {result.missing_fields}")
            print_info(f"Shallow fields: {result.shallow_fields}")
            print_info(f"Errors: {result.content_errors}")

        # 检查是否正确检测为无效
        passed = not result.valid  # 应该返回无效

        if passed:
            print_success("Invalid output correctly detected")
            print_info(f"  Missing fields: {len(result.missing_fields)}")
            print_info(f"  Shallow fields: {len(result.shallow_fields)}")
        else:
            print_error("Invalid output was not detected")

        return self.record_result("Invalid Output Detection", passed)

    # =================================================================
    # Test 5: File-based Validation
    # =================================================================
    def test_file_based_validation(self):
        """测试基于文件的验证"""
        print_header("Test 5: File-based Validation")

        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            test_output = {
                "schema_version": "0.1.0",
                "object_type": "execution_record",
                "phase": "skill_execution",
                "execution": {
                    "status": "completed",
                    "timestamp": "2026-04-27T10:30:00Z",
                    "inputs": {
                        "grid_model": "ieee69",
                        "simulator": "pandapower"
                    },
                    "outputs": {
                        "raw_result_path": "runs/test/result.json"
                    }
                },
                "results": {
                    "primary_metrics": {
                        "loss_mw": {
                            "value": 0.198,
                            "unit": "MW"
                        },
                        "improvement": {
                            "value": 11.6,
                            "unit": "%"
                        }
                    }
                },
                "skill_implementation": {
                    "code": {
                        "main_file": "tasks/task003/solver.py",
                        "structure": [
                            {
                                "function": "optimize",
                                "purpose": "Run optimization algorithm to find best compensation",
                                "algorithm": "greedy_search"
                            }
                        ]
                    }
                },
                "failure_capsule": {
                    "known_limitations": [
                        {
                            "limitation": "Only tested on single load scenario",
                            "impact": "Cannot guarantee performance under varying loads",
                            "severity": "medium"
                        }
                    ]
                },
                "next_actions": {
                    "immediate": [
                        {
                            "action": "Test on multiple load scenarios",
                            "rationale": "Need to validate robustness"
                        }
                    ]
                }
            }
            yaml.dump(test_output, f)
            temp_file = f.name

        try:
            result = self.agent.validate_from_file(temp_file, "skill_execution")

            if self.verbose:
                print_info(f"File: {temp_file}")
                print_info(f"Valid: {result.valid}")
                print_info(f"Content length: {result.content_length}")

            passed = True  # 只要能完成验证就算通过
            print_success("File-based validation completed")

        except Exception as e:
            print_error(f"File-based validation failed: {e}")
            passed = False

        finally:
            os.unlink(temp_file)

        return self.record_result("File-based Validation", passed)

    # =================================================================
    # Test 6: Vague Words Detection
    # =================================================================
    def test_vague_words_detection(self):
        """测试禁用词检测"""
        print_header("Test 6: Vague Words Detection")

        test_cases = [
            ("The result is ok", ["ok"]),
            ("Completed successfully", ["completed"]),
            ("Some improvements made", ["some"]),
            ("Network losses decreased by 11.6%", []),
        ]

        all_passed = True
        for text, expected_words in test_cases:
            found = self.agent._check_vague_words(text)

            if expected_words:
                # 应该检测到禁用词
                if found:
                    print_success(f"Detected vague words in: '{text}' -> {found}")
                else:
                    print_error(f"Missed vague words in: '{text}'")
                    all_passed = False
            else:
                # 不应该检测到禁用词
                if found:
                    print_error(f"False positive in: '{text}' -> {found}")
                    all_passed = False
                else:
                    print_success(f"Clean text: '{text}'")

        return self.record_result("Vague Words Detection", all_passed)

    # =================================================================
    # Test 7: Content Depth Check
    # =================================================================
    def test_content_depth_check(self):
        """测试内容深度检查"""
        print_header("Test 7: Content Depth Check")

        test_cases = [
            ("ok", {"min_length": 10}, True, "too short"),
            ("Detailed explanation here", {"min_length": 10}, False, "long enough"),
            ([], {"min_items": 1}, True, "empty list"),
            (["item1", "item2"], {"min_items": 1}, False, "non-empty list"),
            ({}, {}, True, "empty dict"),
        ]

        all_passed = True
        for value, requirements, should_be_shallow, description in test_cases:
            is_shallow, reason = self.agent._is_shallow_content(value, requirements)

            if is_shallow == should_be_shallow:
                print_success(f"Correctly identified: {description}")
            else:
                print_error(f"Incorrect for: {description} (expected shallow={should_be_shallow}, got {is_shallow})")
                all_passed = False

        return self.record_result("Content Depth Check", all_passed)

    # =================================================================
    # Test 8: Quality Score Calculation
    # =================================================================
    def test_quality_score_calculation(self):
        """测试质量分数计算"""
        print_header("Test 8: Quality Score Calculation")

        # 导入质量验证工具
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from verify_research_quality import calculate_quality_score

        # 创建不同质量的验证结果
        test_cases = [
            # (missing, shallow, errors, warnings, length, min_length, expected_range)
            ([], [], [], [], 2000, 1000, (90, 120), "perfect"),
            (["field1"], [], [], [], 2000, 1000, (80, 100), "one missing"),
            (["f1", "f2"], ["f3"], [], [], 1500, 1000, (60, 80), "multiple issues"),
            (["f1", "f2", "f3", "f4", "f5"], [], [], [], 500, 1000, (30, 50), "many missing"),
        ]

        all_passed = True
        for missing, shallow, errors, warnings, length, min_length, expected_range, description in test_cases:
            result = ValidationResult(
                valid=len(missing) == 0 and len(shallow) == 0 and len(errors) == 0,
                phase="test",
                missing_fields=missing,
                shallow_fields=shallow,
                content_errors=errors,
                warnings=warnings,
                content_length=length,
                min_required_length=min_length
            )

            score = calculate_quality_score(result)
            min_expected, max_expected = expected_range

            if min_expected <= score <= max_expected:
                print_success(f"{description}: score={score:.1f} (expected {min_expected}-{max_expected})")
            else:
                print_error(f"{description}: score={score:.1f} (expected {min_expected}-{max_expected})")
                all_passed = False

        return self.record_result("Quality Score Calculation", all_passed)

    # =================================================================
    # Test 9: Harness Engine Import
    # =================================================================
    def test_harness_engine_import(self):
        """测试 Harness 引擎导入"""
        print_header("Test 9: Harness Engine Import")

        try:
            # 尝试导入增强版引擎
            sys.path.insert(0, str(REPO_ROOT / "scripts"))
            from run_generic_loop_engine_with_harness import (
                GenericLoopEngineWithHarness,
                PhaseConfig
            )

            print_success("Successfully imported GenericLoopEngineWithHarness")
            print_info(f"PhaseConfig class available")

            # 检查关键方法
            required_methods = [
                '_load_phase_configs',
                '_prepare_prompt_with_requirements',
                '_call_worker_with_validation',
                '_create_failure_capsule'
            ]

            all_methods = True
            for method in required_methods:
                if hasattr(GenericLoopEngineWithHarness, method):
                    print_success(f"Method available: {method}")
                else:
                    print_error(f"Method missing: {method}")
                    all_methods = False

            return self.record_result("Harness Engine Import", all_methods)

        except ImportError as e:
            print_error(f"Failed to import Harness Engine: {e}")
            return self.record_result("Harness Engine Import", False)

    # =================================================================
    # Test 10: End-to-End Flow
    # =================================================================
    def test_end_to_end_flow(self):
        """测试端到端流程"""
        print_header("Test 10: End-to-End Flow")

        # 创建临时工作目录
        temp_dir = tempfile.mkdtemp(prefix="harness_test_")

        try:
            # 1. 创建测试输出文件
            test_output = {
                "schema_version": "0.1.0",
                "object_type": "execution_record",
                "phase": "skill_execution",
                "execution": {
                    "status": "completed",
                    "timestamp": "2026-04-27T10:30:00Z",
                    "inputs": {
                        "grid_model": "ieee69",
                        "simulator": "pandapower"
                    },
                    "outputs": {
                        "raw_result_path": "runs/test/result.json"
                    }
                },
                "results": {
                    "primary_metrics": {
                        "loss_mw": {"value": 0.198, "unit": "MW"},
                        "improvement": {"value": 11.6, "unit": "%"}
                    }
                },
                "skill_implementation": {
                    "code": {
                        "main_file": "tasks/task003/solver.py",
                        "structure": [
                            {
                                "function": "optimize",
                                "purpose": "Run optimization algorithm",
                                "algorithm": "greedy_search"
                            }
                        ]
                    }
                },
                "failure_capsule": {
                    "known_limitations": [
                        {
                            "limitation": "Only tested on single load scenario",
                            "impact": "Cannot guarantee performance",
                            "severity": "medium"
                        }
                    ]
                },
                "next_actions": {
                    "immediate": [
                        {
                            "action": "Test on multiple load scenarios",
                            "rationale": "Need to validate robustness"
                        }
                    ]
                }
            }

            # 2. 写入文件
            output_file = Path(temp_dir) / "execution_record.yaml"
            with open(output_file, 'w') as f:
                yaml.dump(test_output, f)

            print_success(f"Created test output file: {output_file}")

            # 3. 使用质量验证工具验证
            sys.path.insert(0, str(REPO_ROOT / "scripts"))
            from verify_research_quality import verify_run_directory, format_report

            report = verify_run_directory(Path(temp_dir))

            print_success(f"Quality verification completed")
            print_info(f"Overall score: {report.overall_score:.1f}")
            print_info(f"Phases checked: {report.phases_checked}")
            print_info(f"Phases passed: {report.phases_passed}")

            # 4. 生成报告
            report_text = format_report(report, "markdown")

            if self.verbose:
                print("\nReport preview:")
                print(report_text[:1000])

            passed = report.phases_checked > 0

            if passed:
                print_success("End-to-end flow completed successfully")
            else:
                print_warning("End-to-end flow completed but no phases found")

            return self.record_result("End-to-End Flow", passed)

        except Exception as e:
            print_error(f"End-to-end flow failed: {e}")
            import traceback
            traceback.print_exc()
            return self.record_result("End-to-End Flow", False)

        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)

    # =================================================================
    # Run All Tests
    # =================================================================
    def run_all_tests(self):
        """运行所有测试"""
        print_header("Harness Integration Tests")
        print(f"Repository: {REPO_ROOT}")
        print(f"Started at: {datetime.now().isoformat()}")

        # 准备
        if not self.setup():
            print_error("Setup failed, aborting tests")
            return 1

        # 运行测试
        tests = [
            self.test_schema_loading,
            self.test_phase_requirements_loading,
            self.test_valid_output_validation,
            self.test_invalid_output_detection,
            self.test_file_based_validation,
            self.test_vague_words_detection,
            self.test_content_depth_check,
            self.test_quality_score_calculation,
            self.test_harness_engine_import,
            self.test_end_to_end_flow,
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                print_error(f"Test {test.__name__} crashed: {e}")
                import traceback
                traceback.print_exc()
                self.record_result(test.__name__, False, str(e))

        # 清理
        self.teardown()

        # 打印结果摘要
        self.print_summary()

        # 返回退出码
        failed_count = sum(1 for r in self.test_results if not r["passed"])
        return 0 if failed_count == 0 else 1

    def print_summary(self):
        """打印测试摘要"""
        print_header("Test Summary")

        passed = sum(1 for r in self.test_results if r["passed"])
        failed = sum(1 for r in self.test_results if not r["passed"])
        total = len(self.test_results)

        print(f"Total tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
        print()

        for result in self.test_results:
            status = f"{Colors.GREEN}✓{Colors.RESET}" if result["passed"] else f"{Colors.RED}✗{Colors.RESET}"
            print(f"{status} {result['name']}")
            if not result["passed"] and result.get("details"):
                print(f"    Details: {result['details']}")

        print()
        if failed == 0:
            print(f"{Colors.GREEN}All tests passed!{Colors.RESET}")
        else:
            print(f"{Colors.RED}{failed} test(s) failed{Colors.RESET}")


def main():
    parser = argparse.ArgumentParser(description="Run Harness Integration Tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--test", "-t", help="Run specific test by name")

    args = parser.parse_args()

    test_runner = HarnessIntegrationTest(verbose=args.verbose)

    if args.test:
        # 运行特定测试
        if not test_runner.setup():
            return 1

        test_method = getattr(test_runner, f"test_{args.test}", None)
        if test_method:
            test_method()
        else:
            print(f"Test not found: {args.test}")
            return 1

        test_runner.teardown()
    else:
        # 运行所有测试
        return test_runner.run_all_tests()


if __name__ == "__main__":
    sys.exit(main())
