# Generic Loop Engine Harness 实施计划

> 目标：将研究记录模板要求强制执行到 Generic Loop Engine 中，确保每个 Phase 的输出都是可审查、可追溯、有价值的。

**版本**: 1.0  
**日期**: 2026-04-28  
**负责人**: TBD  
**预计工期**: 2-3 周  
**优先级**: 高

---

## 1. 项目背景与目标

### 1.1 当前问题

当前 Generic Loop Engine 存在"形式大于内容"的问题：

```yaml
# 当前输出示例（问题）
phase: skill_execution
sequence: 3
status: completed
# 没有假设、没有方法、没有数据、没有技能实现细节
```

这导致：
- 导师/审查者无法判断研究质量
- 3个月后无法复现当时的决策
- 技能无法迭代改进（不知道上一版做了什么）
- 研究变成"出工不出力"的应付

### 1.2 目标状态

每个 Phase 输出必须包含：

```yaml
# 目标输出示例（理想）
phase: skill_execution
work_brief:
  hypothesis:
    statement: "..."
    testable_prediction: "..."
  method:
    description: "..."
  skill_implementation:
    code:
      structure: [...]
    design_decisions: [...]
  results:
    primary_metrics: [...]
  failure_capsule:
    known_limitations: [...]
  next_actions:
    immediate: [...]
```

### 1.3 核心设计原则

1. **Harness 控制**: 不是依赖 Agent 自觉，而是在引擎层面强制
2. **Validation 前置**: 进入下一阶段前必须验证当前输出
3. **渐进式要求**: 先强制核心字段，再逐步增加深度
4. **失败即记录**: 即使输出不满足要求，也要记录失败原因

---

## 2. 详细设计

### 2.1 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    Generic Loop Engine                       │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │ Phase Scheduler │→ │ Phase Executor   │→ │ Validator   │ │
│  │                 │  │ (with Harness)   │  │ Agent       │ │
│  └─────────────────┘  └──────────────────┘  └─────────────┘ │
│           │                    │                    │       │
│           ↓                    ↓                    ↓       │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │ Phase Config    │  │ Execution Agent  │  │ Validation  │ │
│  │ (requirements)  │  │ (Skill/Cognition)│  │ Rules       │ │
│  └─────────────────┘  └──────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │ Work Brief YAML  │ ← 强制输出
                    │ (schema-valid)   │
                    └──────────────────┘
```

### 2.2 核心组件

#### 2.2.1 Phase Requirements 配置

**文件**: `configs/phase_requirements.yaml`

```yaml
# Phase 级别强制输出要求
phases:
  skill_change_request:
    description: "生成技能变更请求"
    required_outputs:
      - name: "work_brief"
        schema: "schemas/work_brief.schema.json"
        must_include:
          - "hypothesis.statement"
          - "hypothesis.rationale"
          - "method.description"
          - "method.algorithm.type"
        min_content_length: 500  # 字符数
        
  skill_execution:
    description: "执行技能代码"
    required_outputs:
      - name: "execution_record"
        schema: "schemas/execution_record.schema.json"
        must_include:
          - "execution.inputs"
          - "execution.outputs"
          - "skill_implementation.code.main_file"
          - "skill_implementation.code.structure"
          - "results.primary_metrics"
          - "failure_capsule.known_limitations"
          - "next_actions.immediate"
        min_content_length: 1000
        
  effectiveness_assessment:
    description: "评估效果"
    required_outputs:
      - name: "assessment_packet"
        schema: "schemas/assessment_packet.schema.json"
        must_include:
          - "interpretation.supports_hypothesis"
          - "interpretation.support_evidence"
          - "failure_capsule.local_failures"
          - "next_actions.short_term"
        min_content_length: 800
```

#### 2.2.2 JSON Schema 定义

**文件**: `schemas/work_brief.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Work Brief",
  "description": "研究工作简报，记录假设、方法和执行",
  "required": ["schema_version", "object_type", "phase", "hypothesis", "method"],
  "properties": {
    "schema_version": {
      "type": "string",
      "const": "0.1.0"
    },
    "object_type": {
      "type": "string",
      "const": "work_brief"
    },
    "phase": {
      "type": "string",
      "enum": ["skill_change_request", "skill_execution", "effectiveness_assessment", "cognition_diagnosis"]
    },
    "hypothesis": {
      "type": "object",
      "required": ["statement", "testable_prediction"],
      "properties": {
        "statement": {
          "type": "string",
          "minLength": 50,
          "description": "研究假设陈述"
        },
        "rationale": {
          "type": "string",
          "minLength": 30,
          "description": "假设的理论依据"
        },
        "testable_prediction": {
          "type": "string",
          "minLength": 20,
          "description": "可量化的预测"
        }
      }
    },
    "method": {
      "type": "object",
      "required": ["description", "algorithm"],
      "properties": {
        "description": {
          "type": "string",
          "minLength": 100,
          "description": "方法详细描述"
        },
        "algorithm": {
          "type": "object",
          "required": ["type"],
          "properties": {
            "type": {
              "type": "string",
              "description": "算法类型"
            },
            "steps": {
              "type": "array",
              "items": {"type": "string"},
              "minItems": 1
            }
          }
        }
      }
    },
    "skill_implementation": {
      "$ref": "#/definitions/skill_implementation"
    },
    "results": {
      "$ref": "#/definitions/results"
    },
    "failure_capsule": {
      "$ref": "#/definitions/failure_capsule"
    },
    "next_actions": {
      "$ref": "#/definitions/next_actions"
    }
  },
  "definitions": {
    "skill_implementation": {
      "type": "object",
      "required": ["code"],
      "properties": {
        "code": {
          "type": "object",
          "required": ["main_file", "structure"],
          "properties": {
            "main_file": {"type": "string"},
            "structure": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["function", "purpose", "algorithm"],
                "properties": {
                  "function": {"type": "string"},
                  "purpose": {"type": "string", "minLength": 20},
                  "algorithm": {"type": "string"},
                  "complexity": {"type": "string"},
                  "lines": {"type": "string"}
                }
              }
            }
          }
        },
        "design_decisions": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["decision", "alternatives_considered", "trade_offs"],
            "properties": {
              "decision": {"type": "string"},
              "alternatives_considered": {"type": "array", "items": {"type": "string"}},
              "trade_offs": {"type": "array", "items": {"type": "string"}},
              "validated": {"type": "boolean"}
            }
          }
        },
        "parameters": {
          "type": "object",
          "properties": {
            "tuning_history": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["attempt", "value", "result"],
                "properties": {
                  "attempt": {"type": "integer"},
                  "value": {},
                  "result": {"type": "string"}
                }
              }
            }
          }
        }
      }
    },
    "results": {
      "type": "object",
      "required": ["primary_metrics"],
      "properties": {
        "primary_metrics": {
          "type": "object",
          "minProperties": 2,
          "additionalProperties": {
            "type": "object",
            "required": ["value", "unit"],
            "properties": {
              "value": {"type": "number"},
              "unit": {"type": "string"},
              "context": {"type": "string"}
            }
          }
        }
      }
    },
    "failure_capsule": {
      "type": "object",
      "required": ["known_limitations"],
      "properties": {
        "known_limitations": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["limitation", "impact", "severity"],
            "properties": {
              "limitation": {"type": "string", "minLength": 20},
              "impact": {"type": "string"},
              "severity": {"enum": ["low", "medium", "high", "critical"]}
            }
          }
        },
        "local_failures": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "failure": {"type": "string"},
              "cause_hypothesis": {"type": "string"},
              "mitigation_attempted": {"type": "string"},
              "mitigation_result": {"type": "string"}
            }
          }
        }
      }
    },
    "next_actions": {
      "type": "object",
      "required": ["immediate"],
      "properties": {
        "immediate": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["action", "rationale"],
            "properties": {
              "action": {"type": "string", "minLength": 10},
              "rationale": {"type": "string"},
              "expected_output": {"type": "string"}
            }
          }
        }
      }
    }
  }
}
```

#### 2.2.3 Validation Agent

**文件**: `agents/validation_agent.py`

```python
"""
Validation Agent - 验证 Phase 输出是否符合模板要求
"""

import json
import yaml
from jsonschema import validate, ValidationError
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

@dataclass
class ValidationResult:
    valid: bool
    missing_fields: List[str]
    shallow_fields: List[str]  # 字段存在但内容空洞
    errors: List[str]
    feedback: str  # 给 agent 的反馈
    

class ValidationAgent:
    """验证研究记录是否符合强制要求"""
    
    def __init__(self, schema_dir: str = "schemas"):
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """加载所有 JSON Schema"""
        for schema_file in self.schema_dir.glob("*.schema.json"):
            with open(schema_file) as f:
                schema_name = schema_file.stem.replace(".schema", "")
                self.schemas[schema_name] = json.load(f)
    
    def validate_phase_output(
        self,
        output: Dict[str, Any],
        phase: str,
        requirements: Dict[str, Any]
    ) -> ValidationResult:
        """
        验证 Phase 输出
        
        Args:
            output: Agent 生成的输出
            phase: Phase 名称
            requirements: Phase 要求配置
        
        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        missing_fields = []
        shallow_fields = []
        
        # 1. Schema 验证
        schema_name = requirements.get("schema", "").replace(".json", "").replace("schemas/", "")
        if schema_name in self.schemas:
            try:
                validate(instance=output, schema=self.schemas[schema_name])
            except ValidationError as e:
                errors.append(f"Schema 验证失败: {e.message} at {e.json_path}")
                # 提取缺失字段
                if "required" in str(e.validator):
                    missing_fields.extend(self._extract_missing_fields(e))
        
        # 2. 强制字段检查
        must_include = requirements.get("must_include", [])
        for field_path in must_include:
            if not self._has_field(output, field_path):
                missing_fields.append(field_path)
        
        # 3. 内容深度检查
        for field_path in must_include:
            if self._has_field(output, field_path):
                value = self._get_field(output, field_path)
                if self._is_shallow(value):
                    shallow_fields.append(field_path)
        
        # 4. 最小长度检查
        min_length = requirements.get("min_content_length", 0)
        content_str = yaml.dump(output)
        if len(content_str) < min_length:
            errors.append(f"内容长度 {len(content_str)} 小于要求 {min_length}")
        
        # 5. 生成反馈
        feedback = self._generate_feedback(
            phase, missing_fields, shallow_fields, errors
        )
        
        valid = len(missing_fields) == 0 and len(shallow_fields) == 0 and len(errors) == 0
        
        return ValidationResult(
            valid=valid,
            missing_fields=missing_fields,
            shallow_fields=shallow_fields,
            errors=errors,
            feedback=feedback
        )
    
    def _has_field(self, obj: Dict, path: str) -> bool:
        """检查对象是否包含指定路径的字段"""
        parts = path.split(".")
        current = obj
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        return True
    
    def _get_field(self, obj: Dict, path: str) -> Any:
        """获取指定路径的字段值"""
        parts = path.split(".")
        current = obj
        for part in parts:
            current = current.get(part, {})
        return current
    
    def _is_shallow(self, value: Any) -> bool:
        """检查内容是否过于简略（空洞）"""
        if value is None:
            return True
        if isinstance(value, str):
            # 空字符串或太短
            if len(value.strip()) < 10:
                return True
            # 过于笼统的描述
            vague_words = ["done", "completed", "finished", "ok", "good", "some", "certain"]
            if any(word in value.lower() for word in vague_words):
                return True
        if isinstance(value, list):
            return len(value) == 0
        if isinstance(value, dict):
            return len(value) == 0
        return False
    
    def _extract_missing_fields(self, error: ValidationError) -> List[str]:
        """从 ValidationError 中提取缺失字段"""
        # 简化实现，实际可能需要更复杂的解析
        return []
    
    def _generate_feedback(
        self,
        phase: str,
        missing: List[str],
        shallow: List[str],
        errors: List[str]
    ) -> str:
        """生成给 agent 的反馈"""
        lines = [f"Phase '{phase}' 输出验证失败:"]
        
        if missing:
            lines.append(f"\n缺少强制字段 ({len(missing)} 个):")
            for field in missing:
                lines.append(f"  - {field}")
        
        if shallow:
            lines.append(f"\n内容过于简略 ({len(shallow)} 个):")
            for field in shallow:
                lines.append(f"  - {field}")
        
        if errors:
            lines.append(f"\n其他错误 ({len(errors)} 个):")
            for error in errors:
                lines.append(f"  - {error}")
        
        lines.append("\n请补充上述信息后重试。")
        lines.append("参考模板: docs/IDEAL_RESEARCH_RECORD_TEMPLATE.md")
        
        return "\n".join(lines)
```

#### 2.2.4 修改后的 Generic Loop Engine

**文件**: `scripts/run_generic_loop_engine.py` (修改部分)

```python
"""
Generic Loop Engine - 带强制输出要求的版本
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# 新增导入
from agents.validation_agent import ValidationAgent, ValidationResult


@dataclass
class PhaseConfig:
    """Phase 配置"""
    name: str
    description: str
    required_outputs: list
    schema: str
    must_include: list
    max_retries: int = 3


class GenericLoopEngineWithHarness:
    """
    Generic Loop Engine with Output Validation Harness
    
    核心改进:
    1. 每个 Phase 有强制输出要求
    2. 验证失败时自动重试
    3. 多次失败后记录失败胶囊
    """
    
    def __init__(
        self,
        task_adapter_path: str,
        workspace_root: str,
        config_path: str = "configs/phase_requirements.yaml"
    ):
        self.task_adapter = self._load_yaml(task_adapter_path)
        self.workspace = Path(workspace_root)
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # 新增组件
        self.validation_agent = ValidationAgent()
        self.phase_requirements = self._load_phase_requirements(config_path)
        
        # 执行上下文
        self.context = {
            "current_phase": None,
            "phase_outputs": {},
            "retry_count": 0,
            "max_retries_per_phase": 3
        }
    
    def _load_yaml(self, path: str) -> Dict:
        with open(path) as f:
            return yaml.safe_load(f)
    
    def _load_phase_requirements(self, path: str) -> Dict[str, PhaseConfig]:
        """加载 Phase 要求配置"""
        data = self._load_yaml(path)
        configs = {}
        for phase_name, config in data.get("phases", {}).items():
            configs[phase_name] = PhaseConfig(
                name=phase_name,
                description=config.get("description", ""),
                required_outputs=config.get("required_outputs", []),
                schema=config.get("schema", ""),
                must_include=config.get("must_include", []),
                max_retries=config.get("max_retries", 3)
            )
        return configs
    
    def run_phase(
        self,
        phase: str,
        agent,
        initial_prompt: str
    ) -> Dict[str, Any]:
        """
        执行单个 Phase，带强制验证
        
        Args:
            phase: Phase 名称
            agent: 执行 agent
            initial_prompt: 初始提示
        
        Returns:
            Phase 输出（已验证）
        """
        print(f"\n{'='*60}")
        print(f"Phase: {phase}")
        print(f"{'='*60}")
        
        phase_config = self.phase_requirements.get(phase)
        if not phase_config:
            raise ValueError(f"Unknown phase: {phase}")
        
        # 准备带有输出要求的 prompt
        prompt = self._prepare_prompt_with_requirements(
            initial_prompt, phase_config
        )
        
        # 尝试执行（带重试）
        for attempt in range(phase_config.max_retries):
            print(f"\nAttempt {attempt + 1}/{phase_config.max_retries}")
            
            # 执行 agent
            output = agent.run(prompt)
            
            # 验证输出
            validation = self.validation_agent.validate_phase_output(
                output, phase, phase_config.__dict__
            )
            
            if validation.valid:
                print(f"✅ Phase {phase} 验证通过")
                self._save_phase_output(phase, output)
                return output
            
            print(f"❌ 验证失败: {len(validation.missing_fields)} 字段缺失, "
                  f"{len(validation.shallow_fields)} 字段简略")
            
            # 准备重试 prompt
            prompt = self._prepare_retry_prompt(
                initial_prompt, output, validation, attempt + 1
            )
        
        # 所有重试失败，记录失败胶囊
        print(f"⚠️ Phase {phase} 多次验证失败，记录失败胶囊")
        failure_output = self._create_failure_capsule(
            phase, phase_config, validation
        )
        self._save_phase_output(phase, failure_output, is_failure=True)
        return failure_output
    
    def _prepare_prompt_with_requirements(
        self,
        base_prompt: str,
        phase_config: PhaseConfig
    ) -> str:
        """准备带有输出要求的 prompt"""
        
        requirements_text = f"""
{base_prompt}

================================================================================
强制输出要求 (必须遵守):
================================================================================

你必须生成符合以下 schema 的 YAML 输出: {phase_config.schema}

必须包含以下字段:
"""
        for field in phase_config.must_include:
            requirements_text += f"  - {field}\n"
        
        requirements_text += f"""
要求:
1. 所有标记为 "必须" 的字段必须填写
2. 不能只用 "completed", "done", "ok" 等空泛词汇
3. 必须包含具体数值、代码位置、算法名称
4. hypothesis 必须有可量化的预测
5. results 必须包含至少2个量化指标
6. failure_capsule 必须记录至少1个局限性
7. next_actions 必须包含至少1个具体行动

输出示例 (请参考 docs/IDEAL_RESEARCH_RECORD_TEMPLATE.md):
```yaml
phase: {phase_config.name}
work_brief:
  hypothesis:
    statement: "..."
    testable_prediction: "降低 > 5%"
  skill_implementation:
    code:
      structure:
        - function: "..."
          purpose: "..."
          algorithm: "..."
  # ... 其他字段
```

请确保你的输出可以被验证通过，否则会被要求重试。
"""
        return requirements_text
    
    def _prepare_retry_prompt(
        self,
        base_prompt: str,
        last_output: Dict,
        validation: ValidationResult,
        attempt: int
    ) -> str:
        """准备重试 prompt"""
        return f"""
{base_prompt}

================================================================================
第 {attempt} 次重试 - 上次输出验证失败
================================================================================

{validation.feedback}

请根据上述反馈补充或修改你的输出，然后重试。
注意:
1. 不要省略任何强制字段
2. 提供具体数值而非空泛描述
3. 记录你的局限性（即使认为结果是成功的）
"""
    
    def _create_failure_capsule(
        self,
        phase: str,
        phase_config: PhaseConfig,
        last_validation: ValidationResult
    ) -> Dict[str, Any]:
        """创建失败胶囊"""
        return {
            "schema_version": "0.1.0",
            "object_type": "phase_failure_capsule",
            "phase": phase,
            "status": "failed_validation",
            "failure_reason": "无法生成符合要求的输出",
            "last_validation": {
                "missing_fields": last_validation.missing_fields,
                "shallow_fields": last_validation.shallow_fields,
                "errors": last_validation.errors
            },
            "next_actions": {
                "immediate": [
                    {
                        "action": f"检查 Phase {phase} 的输入和配置",
                        "rationale": "验证失败可能是输入问题或要求过高"
                    },
                    {
                        "action": "降低输出要求或拆分 Phase",
                        "rationale": "当前要求可能超出 agent 能力"
                    }
                ]
            }
        }
    
    def _save_phase_output(
        self,
        phase: str,
        output: Dict,
        is_failure: bool = False
    ):
        """保存 Phase 输出"""
        suffix = "_failure" if is_failure else ""
        output_path = self.workspace / f"{phase}{suffix}.yaml"
        with open(output_path, 'w') as f:
            yaml.dump(output, f, default_flow_style=False, allow_unicode=True)
        print(f"  输出保存到: {output_path}")
    
    def run(self, loop_config: Dict[str, Any]) -> Path:
        """
        执行完整循环
        
        Args:
            loop_config: 循环配置，包含 phases 列表
        
        Returns:
            最终输出目录
        """
        phases = loop_config.get("phases", [])
        
        for phase_config in phases:
            phase_name = phase_config["name"]
            agent_type = phase_config.get("agent", "default")
            prompt = phase_config.get("prompt", "")
            
            # 获取 agent
            agent = self._get_agent(agent_type)
            
            # 执行 phase（带验证）
            output = self.run_phase(phase_name, agent, prompt)
            
            # 更新上下文
            self.context["phase_outputs"][phase_name] = output
            self.context["current_phase"] = phase_name
        
        return self.workspace
    
    def _get_agent(self, agent_type: str):
        """获取 agent 实例（占位符）"""
        # 实际实现中根据类型返回不同 agent
        from agents.skill_agent import SkillAgent
        return SkillAgent()


# 向后兼容的入口函数
def run_generic_loop_engine(
    task_adapter_path: str,
    workspace_root: str,
    **kwargs
) -> Path:
    """
    向后兼容的入口函数
    
    新增参数:
    - validation_enabled: 是否启用验证 (默认 True)
    - strict_mode: 严格模式，验证失败时停止 (默认 False)
    """
    engine = GenericLoopEngineWithHarness(
        task_adapter_path=task_adapter_path,
        workspace_root=workspace_root
    )
    
    # 构建循环配置
    loop_config = {
        "phases": [
            {
                "name": "skill_change_request",
                "agent": "skill_coder",
                "prompt": "Generate skill change request"
            },
            {
                "name": "skill_execution", 
                "agent": "skill_executor",
                "prompt": "Execute the skill code"
            },
            {
                "name": "effectiveness_assessment",
                "agent": "evaluator",
                "prompt": "Assess the effectiveness"
            }
        ]
    }
    
    return engine.run(loop_config)
```

---

## 3. 实施步骤

### Phase 1: 基础设施 (Week 1)

#### Week 1, Day 1-2: Schema 定义
- [ ] 创建 `schemas/work_brief.schema.json`
- [ ] 创建 `schemas/execution_record.schema.json`
- [ ] 创建 `schemas/assessment_packet.schema.json`
- [ ] 创建 `schemas/skill_implementation.schema.json`

**验收标准**:
```bash
python3 -c "import jsonschema; jsonschema.validate(...)"  # 所有 schema 可加载
python3 scripts/validate_schemas.py  # 验证通过
```

#### Week 1, Day 3-4: Phase Requirements 配置
- [ ] 创建 `configs/phase_requirements.yaml`
- [ ] 定义 skill_change_request 要求
- [ ] 定义 skill_execution 要求
- [ ] 定义 effectiveness_assessment 要求

**验收标准**:
```bash
python3 -c "import yaml; yaml.safe_load(open('configs/phase_requirements.yaml'))"
```

#### Week 1, Day 5: Validation Agent
- [ ] 创建 `agents/validation_agent.py`
- [ ] 实现 schema 验证
- [ ] 实现强制字段检查
- [ ] 实现内容深度检查
- [ ] 编写单元测试

**验收标准**:
```bash
pytest tests/test_validation_agent.py -v  # 所有测试通过
```

### Phase 2: Engine 改造 (Week 2)

#### Week 2, Day 1-2: 核心类实现
- [ ] 创建 `GenericLoopEngineWithHarness` 类
- [ ] 实现 `_prepare_prompt_with_requirements()`
- [ ] 实现 `_prepare_retry_prompt()`
- [ ] 实现 `_create_failure_capsule()`

**验收标准**:
```bash
python3 -c "from scripts.run_generic_loop_engine import GenericLoopEngineWithHarness; ..."  # 可导入
```

#### Week 2, Day 3-4: Phase 执行逻辑
- [ ] 实现 `run_phase()` 带验证逻辑
- [ ] 实现重试机制
- [ ] 实现失败胶囊生成
- [ ] 集成 Validation Agent

**验收标准**:
```python
# 伪代码测试
engine = GenericLoopEngineWithHarness(...)
result = engine.run_phase("skill_execution", mock_agent, "test prompt")
assert "work_brief" in result or "failure_capsule" in result
```

#### Week 2, Day 5: 集成测试
- [ ] 编写集成测试用例
- [ ] 测试正常流程
- [ ] 测试验证失败重试流程
- [ ] 测试多次失败记录失败胶囊流程

**验收标准**:
```bash
pytest tests/test_generic_loop_engine_harness.py -v  # 所有测试通过
```

### Phase 3: 验证与文档 (Week 3)

#### Week 3, Day 1-2: 端到端测试
- [ ] 使用 task003 进行端到端测试
- [ ] 验证输出符合模板
- [ ] 检查所有强制字段存在

**验收标准**:
```bash
python3 scripts/run_generic_loop_engine.py \
  --task-adapter adapters/task003.yaml \
  --workspace-root runs/task003/test_harness_001

# 检查输出文件
ls runs/task003/test_harness_001/skill_execution.yaml
# 验证内容
cat runs/task003/test_harness_001/skill_execution.yaml | grep "skill_implementation"
```

#### Week 3, Day 3: 质量验证工具
- [ ] 创建 `scripts/verify_research_quality.py`
- [ ] 检查所有必需字段
- [ ] 检查内容深度
- [ ] 生成质量报告

**验收标准**:
```bash
python3 scripts/verify_research_quality.py \
  --run-dir runs/task003/test_harness_001 \
  --output report.yaml
# report.yaml 显示所有检查通过
```

#### Week 3, Day 4-5: 文档更新
- [ ] 更新 `docs/IDEAL_RESEARCH_RECORD_TEMPLATE.md`
- [ ] 创建 `docs/HARNESS_USAGE.md`
- [ ] 更新 `AGENTS.md` 相关章节
- [ ] 编写示例代码

**验收标准**:
```bash
# 文档完整性检查
ls docs/HARNESS_USAGE.md
grep "skill_implementation" docs/IDEAL_RESEARCH_RECORD_TEMPLATE.md
```

---

## 4. 验收标准

### 4.1 功能验收

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| Schema 可加载 | `python3 scripts/validate_schemas.py` | 无错误 |
| Validation Agent 工作 | `pytest tests/test_validation_agent.py` | 100% 通过 |
| 强制字段检查 | 提交缺少字段的输出，检查是否被拒绝 | 被拒绝 |
| 重试机制 | 检查失败后的重试次数 | 最多3次 |
| 失败胶囊 | 多次失败后检查是否生成失败胶囊 | 生成且内容完整 |
| 真实任务运行 | 使用 task003 运行 | 输出符合模板 |
| 质量验证工具 | `verify_research_quality.py` | 所有检查通过 |

### 4.2 性能验收

| 指标 | 要求 |
|------|------|
| Validation 耗时 | < 100ms / phase |
| 重试延迟 | 不增加显著延迟 |
| 输出文件大小 | 不限制，但警告 > 10MB |

### 4.3 向后兼容

- [ ] 旧的 `run_generic_loop_engine()` 入口仍然可用
- [ ] 现有 task (001-005) 可以正常执行
- [ ] 可以选择关闭验证 (`validation_enabled=false`)

---

## 5. 风险与缓解

### 风险 1: Agent 无法生成符合要求的输出

**风险描述**: LLM Agent 可能无法一次性（甚至在多次重试后）生成符合所有强制字段的输出。

**缓解措施**:
1. **渐进式要求**: 第一阶段只要求核心字段（hypothesis, method, results）
2. **可选字段**: 将 skill_implementation.design_decisions 设为可选
3. **模板示例**: 在 prompt 中提供详细示例
4. **人机协作**: 验证失败次数过多时，转人工审查

### 风险 2: 验证过于严格导致流程阻塞

**风险描述**: 过于严格的验证可能导致研究流程频繁中断，降低效率。

**缓解措施**:
1. **严格模式开关**: `strict_mode=false` 时允许继续，只记录警告
2. **字段分级**: required vs recommended vs optional
3. **定期调优**: 根据实际运行情况调整验证规则

### 风险 3: 性能开销

**风险描述**: 每个 phase 增加验证步骤，可能显著增加总耗时。

**缓解措施**:
1. **轻量级验证**: 只检查字段存在性和内容长度，不做深度语义分析
2. **异步验证**: 考虑后台验证，不阻塞主流程
3. **缓存**: 验证结果缓存，避免重复验证相同内容

### 风险 4: Schema 变更维护成本

**风险描述**: 模板要求可能随时间变化，维护多个 schema 版本成本高。

**缓解措施**:
1. **版本控制**: schema_version 字段
2. **向后兼容**: 新字段默认为可选
3. **迁移工具**: 提供旧格式到新格式的转换脚本

---

## 6. 相关文件清单

### 新建文件

```
configs/
└── phase_requirements.yaml          # Phase 要求配置

schemas/
├── work_brief.schema.json           # 工作简报 schema
├── execution_record.schema.json     # 执行记录 schema
├── assessment_packet.schema.json    # 评估报告 schema
└── skill_implementation.schema.json # 技能实现 schema

agents/
└── validation_agent.py              # 验证 agent

tests/
├── test_validation_agent.py         # 验证 agent 单元测试
├── test_generic_loop_engine_harness.py  # 集成测试
└── fixtures/
    ├── valid_work_brief.yaml        # 有效输出示例
    └── invalid_work_brief.yaml      # 无效输出示例

scripts/
└── verify_research_quality.py       # 质量验证工具

docs/
├── IDEAL_RESEARCH_RECORD_TEMPLATE.md    # 理想模板 (已存在)
└── HARNESS_USAGE.md                 # Harness 使用指南
```

### 修改文件

```
scripts/
└── run_generic_loop_engine.py       # 核心修改

plans/
└── GENERIC_FRAMEWORK_ROADMAP.md     # 更新进度
```

---

## 7. 参考资源

### 设计参考
- `docs/IDEAL_RESEARCH_RECORD_TEMPLATE.md` - 理想研究记录模板
- `/home/chenying/root-research/AutoResearchFlow/docs/AGENT_EXECUTION_PROTOCOL.md` - AutoResearchFlow 执行协议
- `/home/chenying/root-research/AutoResearchFlow/docs/RESEARCH_HARNESS_PROTOCOL.md` - AutoResearchFlow Harness 协议
- `/home/chenying/root-research/AutoResearchClaw/config.researchclaw.example.yaml` - AutoResearchClaw 配置示例

### 技术参考
- JSON Schema 规范: https://json-schema.org/
- Python jsonschema 库: https://python-jsonschema.readthedocs.io/
- YAML 规范: https://yaml.org/

---

## 8. 附录

### 附录 A: 术语表

| 术语 | 定义 |
|------|------|
| **Harness** | 框架层面的控制和验证机制 |
| **Phase** | 研究循环中的一个阶段（如 skill_execution） |
| **Work Brief** | 工作简报，记录假设、方法和执行 |
| **Failure Capsule** | 失败胶囊，记录局限性和失败点 |
| **Validation Agent** | 专门负责验证输出是否符合要求的 agent |
| **Schema** | JSON Schema，定义数据结构规范 |

### 附录 B: 变更日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-04-28 | 初始版本 |

---

**计划制定**: Claude  
**审核**: 待定  
**批准**: 待定
