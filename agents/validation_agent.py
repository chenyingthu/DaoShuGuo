#!/usr/bin/env python3
"""
Validation Agent - 验证 Phase 输出是否符合模板要求

Usage:
    python3 agents/validation_agent.py --input runs/task003/run_001/execution_record.yaml --phase skill_execution
"""

import json
import yaml
import re
from jsonschema import Draft7Validator
from referencing import Registry, Resource
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import argparse
import sys


@dataclass
class FieldValidationResult:
    """单个字段验证结果"""
    field_path: str
    exists: bool
    is_shallow: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """完整验证结果"""
    valid: bool
    phase: str
    missing_fields: List[str] = field(default_factory=list)
    shallow_fields: List[str] = field(default_factory=list)
    content_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field_results: List[FieldValidationResult] = field(default_factory=list)
    feedback: str = ""
    content_length: int = 0
    min_required_length: int = 0


class ValidationAgent:
    """
    验证研究记录是否符合强制要求

    支持：
    1. JSON Schema 验证
    2. 强制字段检查
    3. 内容深度检查
    4. 禁用词检查
    5. 数值完整性检查
    """

    # 禁用词列表（过于空泛的词汇）
    VAGUE_WORDS = [
        "done", "completed", "finished", "ok", "good",
        "some", "certain", "maybe", "might", "could",
        "etc", "...", "various", "several", "few"
    ]

    # 量词模式（用于检查 testable_prediction）
    QUANTIFIABLE_PATTERNS = [r'>', r'<', r'=', r'%', r'percent', r'times', r'\d+']

    def __init__(self, schema_dir: str = "schemas", config_path: str = "configs/phase_requirements.yaml"):
        """
        初始化 Validation Agent

        Args:
            schema_dir: Schema 文件目录
            config_path: Phase 要求配置文件路径
        """
        self.schema_dir = Path(schema_dir)
        self.config_path = Path(config_path)
        self.schemas: Dict[str, Dict] = {}
        self.phase_requirements: Dict[str, Dict] = {}
        self.global_config: Dict = {}

        self._load_schemas()
        self._load_phase_requirements()

    def _load_schemas(self):
        """加载所有 JSON Schema"""
        if not self.schema_dir.exists():
            raise FileNotFoundError(f"Schema directory not found: {self.schema_dir}")

        for schema_file in self.schema_dir.glob("*.schema.json"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_name = schema_file.stem.replace(".schema", "")
                    self.schemas[schema_name] = json.load(f)
                    print(f"[ValidationAgent] Loaded schema: {schema_name}")
            except json.JSONDecodeError as e:
                print(f"[ValidationAgent] Warning: Failed to parse {schema_file}: {e}")

    def _load_phase_requirements(self):
        """加载 Phase 要求配置"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Phase requirements config not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.phase_requirements = config.get("phases", {})
            self.global_config = {
                "vague_words": config.get("global_validation", {}).get("vague_words", self.VAGUE_WORDS),
                "retry_policy": config.get("retry_policy", {}),
                "naming_conventions": config.get("naming_conventions", {})
            }
            print(f"[ValidationAgent] Loaded {len(self.phase_requirements)} phase requirements")

    def validate_phase_output(
        self,
        output: Dict[str, Any],
        phase: str,
        requirements: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        验证 Phase 输出

        Args:
            output: Agent 生成的输出
            phase: Phase 名称
            requirements: Phase 要求配置（可选，默认从配置文件加载）

        Returns:
            ValidationResult: 验证结果
        """
        if requirements is None:
            requirements = self.phase_requirements.get(phase, {})

        if not requirements:
            return ValidationResult(
                valid=False,
                phase=phase,
                content_errors=[f"No requirements found for phase: {phase}"],
                feedback=f"未找到 Phase '{phase}' 的配置"
            )

        missing_fields = []
        shallow_fields = []
        content_errors = []
        warnings = []
        field_results = []

        # 1. Schema 验证
        schema_errors = self._validate_schema(output, requirements)
        content_errors.extend(schema_errors)

        # 2. 强制字段检查
        must_include = requirements.get("must_include", [])
        for field_path in must_include:
            field_result = self._validate_field(output, field_path, requirements)
            field_results.append(field_result)

            if not field_result.exists:
                missing_fields.append(field_path)
            elif field_result.is_shallow:
                shallow_fields.append(field_path)

            if field_result.errors:
                content_errors.extend(field_result.errors)
            if field_result.warnings:
                warnings.extend(field_result.warnings)

        # 3. 内容长度检查
        content_length = len(yaml.dump(output, allow_unicode=True))
        min_length = requirements.get("min_content_length", 0)
        length_error = self._validate_content_length(content_length, min_length)
        if length_error:
            content_errors.append(length_error)

        # 4. 特殊字段深度验证
        special_errors = self._validate_special_fields(output, requirements)
        content_errors.extend(special_errors)

        # 5. 生成反馈
        valid = len(missing_fields) == 0 and len(shallow_fields) == 0 and len(content_errors) == 0
        feedback = self._generate_feedback(
            phase, requirements, missing_fields, shallow_fields,
            content_errors, warnings, content_length, min_length
        )

        return ValidationResult(
            valid=valid,
            phase=phase,
            missing_fields=missing_fields,
            shallow_fields=shallow_fields,
            content_errors=content_errors,
            warnings=warnings,
            field_results=field_results,
            feedback=feedback,
            content_length=content_length,
            min_required_length=min_length
        )

    def _validate_schema(self, output: Dict[str, Any], requirements: Dict[str, Any]) -> List[str]:
        """验证 JSON Schema"""
        errors = []
        schema_path = requirements.get("schema", "")
        if not schema_path:
            required_outputs = requirements.get("required_outputs", [])
            if required_outputs and isinstance(required_outputs[0], dict):
                schema_path = required_outputs[0].get("schema", "")
        schema_name = schema_path.replace("schemas/", "").replace(".schema.json", "")

        if schema_name in self.schemas:
            try:
                schema = self.schemas[schema_name]
                resources = []
                for name, loaded_schema in self.schemas.items():
                    filename = f"{name}.schema.json"
                    schema_file = self.schema_dir / filename
                    if schema_file.exists():
                        resources.append((schema_file.resolve().as_uri(), Resource.from_contents(loaded_schema)))
                        resources.append((filename, Resource.from_contents(loaded_schema)))
                registry = Registry().with_resources(resources)
                validator = Draft7Validator(schema, registry=registry)
                for error in validator.iter_errors(output):
                    errors.append(f"Schema validation: {error.message} at {error.json_path}")
            except Exception as e:
                errors.append(f"Schema validation failed to run: {e}")

        return errors

    def _validate_field(
        self,
        obj: Dict[str, Any],
        field_path: str,
        requirements: Dict[str, Any]
    ) -> FieldValidationResult:
        """验证单个字段"""
        parts = field_path.split(".")
        current = obj
        exists = True

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                exists = False
                break

        result = FieldValidationResult(field_path=field_path, exists=exists)

        if not exists:
            return result

        # 检查内容是否过于简略
        field_requirements = self._get_field_requirements(field_path, requirements)
        is_shallow, shallow_reason = self._is_shallow_content(current, field_requirements)
        result.is_shallow = is_shallow

        if is_shallow:
            result.errors.append(f"Content too shallow: {shallow_reason}")

        # 检查禁用词
        vague_words_found = self._check_vague_words(current)
        if vague_words_found:
            result.warnings.append(f"Vague words detected: {vague_words_found}")

        # 特殊字段检查
        special_errors = self._check_special_field(field_path, current, field_requirements)
        result.errors.extend(special_errors)

        return result

    def _get_field_requirements(self, field_path: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """获取字段特定要求"""
        field_requirements = requirements.get("field_requirements", {})
        return field_requirements.get(field_path, {})

    def _is_shallow_content(self, value: Any, field_requirements: Dict[str, Any]) -> Tuple[bool, str]:
        """检查内容是否过于简略"""
        min_length = field_requirements.get("min_length", 0)

        if value is None:
            return True, "Value is None"

        if isinstance(value, str):
            if len(value.strip()) < min_length:
                return True, f"String length {len(value)} < {min_length}"
            if min_length > 0 and value.strip().lower() in ["done", "completed", "ok", "finished"]:
                return True, f"Too generic: '{value}'"

        if isinstance(value, list):
            if len(value) == 0:
                return True, "Empty list"
            min_items = field_requirements.get("min_items", 0)
            if len(value) < min_items:
                return True, f"List items {len(value)} < {min_items}"

        if isinstance(value, dict):
            if len(value) == 0:
                return True, "Empty dict"

            # 检查必需子字段
            required_children = field_requirements.get("each_item_must_have", [])
            if required_children:
                for key, child in value.items():
                    if isinstance(child, dict):
                        for req_field in required_children:
                            if req_field not in child:
                                return True, f"Missing required field '{req_field}' in '{key}'"

        return False, ""

    def _check_vague_words(self, value: Any) -> List[str]:
        """检查禁用词"""
        found = []
        text = str(value).lower()

        for word in self.global_config.get("vague_words", self.VAGUE_WORDS):
            if word.lower() in text:
                found.append(word)

        return found

    def _check_special_field(self, field_path: str, value: Any, field_requirements: Dict[str, Any]) -> List[str]:
        """特殊字段检查"""
        errors = []

        # testable_prediction 必须包含可量化指标
        if "testable_prediction" in field_path:
            if field_requirements.get("must_contain_quantifiable", False):
                has_quantifiable = False
                text = str(value)
                for pattern in self.QUANTIFIABLE_PATTERNS:
                    if re.search(pattern, text):
                        has_quantifiable = True
                        break
                if not has_quantifiable:
                    errors.append(f"Field '{field_path}' must contain quantifiable metrics (e.g., >5%, <10)")

        # method.description 必须包含算法名称
        if field_path == "method.description":
            if field_requirements.get("must_contain_algorithm_name", False):
                # 简单启发式：检查是否包含大写字母（可能为算法名称）
                if not re.search(r'[A-Z]{2,}', str(value)):
                    errors.append(f"Field '{field_path}' should mention algorithm name (e.g., 'Greedy Algorithm', 'Particle Swarm')")

        return errors

    def _validate_content_length(self, content_length: int, min_required: int) -> Optional[str]:
        """验证内容长度"""
        if min_required > 0 and content_length < min_required:
            return f"Content length {content_length} < minimum required {min_required}"
        return None

    def _validate_special_fields(self, output: Dict[str, Any], requirements: Dict[str, Any]) -> List[str]:
        """验证特殊字段组合"""
        errors = []

        # 检查结果中是否所有数值都有单位
        results = output.get("results", {})
        primary_metrics = results.get("primary_metrics", {})

        for metric_name, metric_data in primary_metrics.items():
            if isinstance(metric_data, dict):
                if "value" in metric_data and "unit" not in metric_data:
                    errors.append(f"Metric '{metric_name}' has value but no unit")

        return errors

    def _generate_feedback(
        self,
        phase: str,
        requirements: Dict[str, Any],
        missing: List[str],
        shallow: List[str],
        errors: List[str],
        warnings: List[str],
        content_length: int,
        min_required: int
    ) -> str:
        """生成给 agent 的反馈"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"Phase '{phase}' 输出验证报告")
        lines.append("=" * 70)

        # 总体状态
        if not missing and not shallow and not errors:
            lines.append("\n✅ 验证通过")
        else:
            lines.append("\n❌ 验证失败")

        lines.append(f"\n内容长度: {content_length} 字符 (要求: {min_required}+)")

        # 缺失字段
        if missing:
            lines.append(f"\n⚠️  缺少强制字段 ({len(missing)} 个):")
            for field in missing:
                lines.append(f"   - {field}")

        # 内容简略字段
        if shallow:
            lines.append(f"\n⚠️  内容过于简略 ({len(shallow)} 个):")
            for field in shallow:
                lines.append(f"   - {field}")

        # 内容错误
        if errors:
            lines.append(f"\n⚠️  内容错误 ({len(errors)} 个):")
            for error in errors[:5]:  # 最多显示5个
                lines.append(f"   - {error}")
            if len(errors) > 5:
                lines.append(f"   ... 还有 {len(errors) - 5} 个错误")

        # 警告
        if warnings:
            lines.append(f"\n⚠️  警告 ({len(warnings)} 个):")
            for warning in warnings[:3]:
                lines.append(f"   - {warning}")

        # 改进建议
        lines.append("\n" + "=" * 70)
        lines.append("改进建议:")
        lines.append("=" * 70)

        if missing:
            lines.append("\n1. 补充缺失的强制字段")
            lines.append("   参考模板: docs/IDEAL_RESEARCH_RECORD_TEMPLATE.md")

        if shallow:
            lines.append("\n2. 扩展简略字段的内容")
            lines.append("   - 提供具体数值而非空泛描述")
            lines.append("   - 说明算法名称和复杂度")
            lines.append("   - 记录决策理由和替代方案")

        if "failure_capsule" in str(shallow) or "failure_capsule" in str(missing):
            lines.append("\n3. 务必记录失败胶囊 (failure_capsule)")
            lines.append("   - 即使研究'成功'，也要记录已知局限性")
            lines.append("   - 这体现了研究的严谨性")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)

    def validate_from_file(self, file_path: str, phase: str) -> ValidationResult:
        """从文件加载并验证"""
        path = Path(file_path)
        if not path.exists():
            return ValidationResult(
                valid=False,
                phase=phase,
                content_errors=[f"File not found: {file_path}"]
            )

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 尝试解析 YAML 或 JSON
        try:
            output = yaml.safe_load(content)
        except yaml.YAMLError:
            try:
                output = json.loads(content)
            except json.JSONDecodeError:
                return ValidationResult(
                    valid=False,
                    phase=phase,
                    content_errors=[f"Failed to parse {file_path} as YAML or JSON"]
                )

        return self.validate_phase_output(output, phase)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Validate research phase output against requirements"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input YAML/JSON file to validate"
    )
    parser.add_argument(
        "--phase", "-p",
        required=True,
        choices=["skill_change_request", "skill_execution", "effectiveness_assessment", "cognition_diagnosis", "skill_coding"],
        help="Phase type"
    )
    parser.add_argument(
        "--schema-dir", "-s",
        default="schemas",
        help="Schema directory (default: schemas)"
    )
    parser.add_argument(
        "--config", "-c",
        default="configs/phase_requirements.yaml",
        help="Phase requirements config (default: configs/phase_requirements.yaml)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Quiet mode, only output result code"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output result as JSON"
    )

    args = parser.parse_args()

    try:
        agent = ValidationAgent(
            schema_dir=args.schema_dir,
            config_path=args.config
        )

        result = agent.validate_from_file(args.input, args.phase)

        if args.json:
            output = {
                "valid": result.valid,
                "phase": result.phase,
                "missing_fields": result.missing_fields,
                "shallow_fields": result.shallow_fields,
                "errors": result.content_errors,
                "warnings": result.warnings,
                "content_length": result.content_length,
                "min_required_length": result.min_required_length
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        elif not args.quiet:
            print(result.feedback)

        sys.exit(0 if result.valid else 1)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
