"""
Validation Agent 单元测试

Usage:
    pytest tests/test_validation_agent.py -v
"""

import pytest
import yaml
import json
from pathlib import Path
from agents.validation_agent import ValidationAgent, ValidationResult


class TestValidationAgent:
    """Validation Agent 测试类"""

    @pytest.fixture
    def agent(self):
        """创建 Validation Agent 实例"""
        return ValidationAgent(
            schema_dir="schemas",
            config_path="configs/phase_requirements.yaml"
        )

    @pytest.fixture
    def valid_work_brief(self):
        """有效的工作简报示例"""
        return {
            "schema_version": "0.1.0",
            "object_type": "work_brief",
            "phase": "skill_execution",
            "sequence": 1,
            "hypothesis": {
                "statement": "在IEEE69网络的高电压偏差节点添加无功补偿，可以降低网损并改善电压分布",
                "rationale": "基于无功功率-电压耦合关系，Q注入可减少线路无功传输",
                "testable_prediction": "补偿后网损降低>5%，电压偏差改善>10%"
            },
            "method": {
                "name": "weak_node_reactive_compensation",
                "description": "识别电压最低的三个节点，添加并联电容器进行无功补偿。使用贪心算法逐步增加补偿量直到满足约束。",
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
                "code_location": "tasks/task003/candidate_solver.py:45-89",
                "baseline_comparison": "与无补偿基线对比"
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
                        "impact": "无法评估负荷波动下的性能稳定性",
                        "severity": "medium"
                    }
                ],
                "local_failures": [],
                "generalizability_gaps": [
                    "仅在IEEE69上测试"
                ]
            },
            "next_actions": {
                "immediate": [
                    {
                        "action": "测试不同补偿位置组合",
                        "rationale": "当前固定位置可能非最优",
                        "expected_output": "位置敏感性分析报告"
                    }
                ]
            }
        }

    @pytest.fixture
    def invalid_work_brief_shallow(self):
        """内容过于简略的无效示例"""
        return {
            "schema_version": "0.1.0",
            "object_type": "work_brief",
            "phase": "skill_execution",
            "hypothesis": {
                "statement": "补偿可以降低损耗",
                "testable_prediction": "变好"
            },
            "method": {
                "description": "使用算法进行优化",
                "algorithm": {
                    "type": "optimization"
                }
            },
            "results": {
                "primary_metrics": {}
            },
            "failure_capsule": {
                "known_limitations": []
            },
            "next_actions": {
                "immediate": []
            }
        }

    @pytest.fixture
    def invalid_work_brief_missing(self):
        """缺少强制字段的无效示例"""
        return {
            "schema_version": "0.1.0",
            "object_type": "work_brief",
            "phase": "skill_execution",
            "hypothesis": {
                "statement": "在IEEE69网络添加无功补偿"
            },
            "method": {
                "description": "识别电压节点并添加补偿"
            }
        }

    def test_load_schemas(self, agent):
        """测试 Schema 加载"""
        assert len(agent.schemas) > 0
        assert "work_brief" in agent.schemas

    def test_load_phase_requirements(self, agent):
        """测试 Phase 配置加载"""
        assert len(agent.phase_requirements) > 0
        assert "skill_execution" in agent.phase_requirements

    def test_validate_valid_work_brief(self, agent, valid_work_brief):
        """测试验证有效的工作简报"""
        result = agent.validate_phase_output(
            valid_work_brief,
            "skill_execution"
        )

        # 检查结果结构
        assert isinstance(result, ValidationResult)
        assert result.phase == "skill_execution"
        assert result.content_length > 0

        # 有效内容应该通过（或只有少数警告）
        print(f"\nValidation result for valid work brief:")
        print(f"  Valid: {result.valid}")
        print(f"  Missing fields: {result.missing_fields}")
        print(f"  Shallow fields: {result.shallow_fields}")
        print(f"  Errors: {result.content_errors}")

    def test_validate_shallow_content(self, agent, invalid_work_brief_shallow):
        """测试检测内容过于简略"""
        result = agent.validate_phase_output(
            invalid_work_brief_shallow,
            "skill_execution"
        )

        # 应该检测到简略字段
        assert len(result.shallow_fields) > 0 or len(result.content_errors) > 0

        # 检查反馈包含建议
        assert "改进建议" in result.feedback

        print(f"\nValidation result for shallow content:")
        print(f"  Shallow fields: {result.shallow_fields}")

    def test_validate_missing_fields(self, agent, invalid_work_brief_missing):
        """测试检测缺失字段"""
        result = agent.validate_phase_output(
            invalid_work_brief_missing,
            "skill_execution"
        )

        # 应该检测到缺失字段
        assert len(result.missing_fields) > 0

        print(f"\nValidation result for missing fields:")
        print(f"  Missing fields: {result.missing_fields}")

    def test_check_vague_words(self, agent):
        """测试禁用词检测"""
        # 包含禁用词的文本
        text_with_vague = "The result is ok and good, maybe some improvement"
        found = agent._check_vague_words(text_with_vague)

        assert len(found) > 0
        assert "ok" in [w.lower() for w in found]

        # 干净的文本
        text_clean = "Network losses decreased by 11.6% from 0.224 MW to 0.198 MW"
        found_clean = agent._check_vague_words(text_clean)
        assert len(found_clean) == 0

    def test_is_shallow_content(self, agent):
        """测试内容深度检查"""
        # 过于简短的字符串
        is_shallow, reason = agent._is_shallow_content("ok", {"min_length": 10})
        assert is_shallow is True

        # 足够长的字符串
        is_shallow, reason = agent._is_shallow_content(
            "This is a detailed explanation of the algorithm used",
            {"min_length": 10}
        )
        assert is_shallow is False

        # 空列表
        is_shallow, reason = agent._is_shallow_content([], {"min_items": 1})
        assert is_shallow is True

    def test_special_field_checks(self, agent):
        """测试特殊字段检查"""
        # testable_prediction 必须包含量词
        field_requirements = {"must_contain_quantifiable": True}
        errors = agent._check_special_field(
            "hypothesis.testable_prediction",
            "网损会降低",
            field_requirements
        )
        assert len(errors) > 0

        # 包含量词应该通过
        errors = agent._check_special_field(
            "hypothesis.testable_prediction",
            "网损降低>5%",
            field_requirements
        )
        assert len(errors) == 0

    def test_generate_feedback(self, agent):
        """测试反馈生成"""
        feedback = agent._generate_feedback(
            phase="skill_execution",
            requirements={"min_content_length": 1000},
            missing=["results.primary_metrics"],
            shallow=["hypothesis.statement"],
            errors=["Content length too short"],
            warnings=["Vague words detected"],
            content_length=500,
            min_required=1000
        )

        # 反馈应该包含关键信息
        assert "skill_execution" in feedback
        assert "缺少强制字段" in feedback or "missing" in feedback.lower()
        assert "改进建议" in feedback

    def test_content_length_validation(self, agent):
        """测试内容长度验证"""
        # 长度不足
        error = agent._validate_content_length(500, 1000)
        assert error is not None
        assert "500" in error
        assert "1000" in error

        # 长度满足
        error = agent._validate_content_length(1500, 1000)
        assert error is None


class TestValidationIntegration:
    """集成测试"""

    def test_end_to_end_validation(self, tmp_path):
        """测试端到端验证流程"""
        # 创建测试文件
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

        # 写入临时文件
        test_file = tmp_path / "test_output.yaml"
        with open(test_file, 'w') as f:
            yaml.dump(test_output, f)

        # 验证
        agent = ValidationAgent()
        result = agent.validate_from_file(str(test_file), "skill_execution")

        assert isinstance(result, ValidationResult)
        assert result.phase == "skill_execution"

        print(f"\nEnd-to-end validation result:")
        print(f"  Valid: {result.valid}")
        print(f"  Content length: {result.content_length}")
        if not result.valid:
            print(f"  Feedback:\n{result.feedback}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
