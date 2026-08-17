# Recipe 契约

Recipe 定义一个产物的目标、受众、输入边界、必需内容、组织结构和验收规则。Recipe 不负责全库检索，也不保存事实。

## 最小内容

```yaml
recipe_name:
recipe_version:
purpose:
audience:
required_context: []
optional_context: []
output_structure: []
evidence_requirements: []
forbidden_content: []
quality_checks: []
output_format:
```

## 设计原则

- 一个 Recipe 对应稳定的阅读或决策任务，不对应某个具体对象。
- 必需信息必须能够从上下文包获得。
- 缺失必需信息时应披露缺口、生成待补项或停止正式化，不得猜测。
- Recipe 可以规定篇幅、层级、语气和表现形式，但不得改变知识性质。
- 产物中的关键结论必须能回溯到上下文包和来源。
- 计划、事实、推断、风险和建议不得混写。

## 产物生成边界

生成阶段允许：

- 组织、压缩和解释上下文；
- 进行 Recipe 明确允许的推导；
- 对未决项给出受限建议；
- 根据 Template 呈现内容。

生成阶段禁止：

- 绕过上下文包搜索全库并静默加入事实；
- 使用未批准变更而不标注；
- 删除冲突或限制；
- 将推断转写为核验事实；
- 产生未授权的承诺、审批或外部动作。

## 新 Recipe 的充分理由

当产物目标、受众、必需证据、组织结构或验收规则实质不同，新增 Recipe。仅措辞、长度或视觉风格变化优先通过参数或 Template 处理。
