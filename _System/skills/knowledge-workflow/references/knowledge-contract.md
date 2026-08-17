# 知识契约

## 目录

1. 目的
2. 规范化知识包
3. 知识原语
4. 时间与范围
5. 信息性质
6. 来源角色
7. 身份与合并
8. 冲突和不确定性

## 1. 目的

本契约定义所有 Reader、Schema、变更建议、对象笔记和 Validator 共同使用的最小语义。它不规定任何具体对象类型或业务字段。

核心公式：

```text
KnowledgeUnit = Subject
              + Predicate
              + ValueOrObject
              + TemporalScope
              + ApplicabilityScope
              + SourceLocator
              + EpistemicStatus
```

任何扩展都可以增加字段，但不得删除或隐式化上述维度。

## 2. 规范化知识包

Reader 的临时输出应包含：

```yaml
source:
  asset_id:
  logical_dataset_id:
  role:
  observed_at:
  effective_scope:
  classification:
  access_scope:

objects: []
assertions: []
events: []
relations: []
matters: []
conflicts: []
quality_flags: []
```

规范化知识包是阶段间契约，默认可以重建，不必永久保存。需要审计、复现或性能保证时，才按批准的保留策略持久化。

## 3. 知识原语

### 3.1 Object

```yaml
uid:
object_type:
canonical_name:
aliases: []
external_ids: []
identity_status: confirmed | provisional | ambiguous
source_locators: []
```

规则：

- `uid` 是项目内部稳定标识，不直接等同于名称。
- `provisional` 对象不得在未确认时与现有对象自动合并。
- 不因单次出现就强制创建对象。

### 3.2 Assertion

```yaml
subject_uid:
predicate:
value:
raw_value:
unit:
precision:
effective_from:
effective_to:
as_of:
period:
scope:
epistemic_status:
source_locator:
confidence:
notes:
```

`value` 是规范化值，`raw_value` 保留来源原始表达。单位、精度、周期或口径不明确时保持空缺并产生质量标记，不得猜测。

### 3.3 Event

```yaml
subject_uid:
event_type:
start_at:
end_at:
date_precision:
description:
participants: []
epistemic_status:
source_locator:
```

事件以追加为主。无法确定准确日期时，记录已知粒度，例如年、月或时间范围。

### 3.4 Relation

```yaml
subject_uid:
relation_type:
object_uid:
effective_from:
effective_to:
epistemic_status:
source_locator:
```

关系有方向。共同出现、名称相似或语义相关不自动构成关系。

### 3.5 Matter

```yaml
matter_id:
subject_uid:
matter_type:
title:
status:
owner:
priority:
due_at:
dependencies: []
completion_evidence: []
source_locator:
```

事项包括需要跟踪的开放工作和已作出的决定。叙述性摘要不得替代事项状态。

### 3.6 Conflict

```yaml
subject_uid:
predicate_or_relation:
candidates: []
reason:
impact:
resolution_status: open | resolved | accepted-difference
resolution_evidence: []
```

冲突是正式知识状态，不是异常文本。不同时间、范围或口径下的差异不一定是冲突，应先拆分适用条件。

## 4. 时间与范围

时间字段含义：

- `observed_at`：来源被观察或接收的时间；
- `effective_from` / `effective_to`：事实或关系生效区间；
- `as_of`：状态快照基准时点；
- `period`：统计或叙述覆盖期间；
- `processed_at`：Agent 处理时间。

禁止用 `processed_at` 替代事实时间。当前状态必须可说明其 `as_of` 或有效区间。

范围至少考虑：

- 主体范围；
- 空间、组织或权限范围；
- 统计口径；
- 版本或规则范围；
- 适用条件。

范围不一致的信息不得直接覆盖。

## 5. 信息性质

允许值：

- `source-stated`：来源直接陈述；
- `verified`：经指定权威来源或人工确认；
- `derived`：通过明确、可复现规则得到；
- `inferred`：Agent 解释、归纳或判断。

升级信息性质必须有证据。例如 `source-stated` 变为 `verified` 时，应记录核验人、核验时间或权威来源。

## 6. 来源角色

- `evidence`：可以提出知识更新；
- `snapshot`：只能在给定时点和范围内解释；
- `view`：用于筛选、分类、聚合或展示，默认不重复更新事实；
- `reference`：用于解释规则、定义和约束；
- `superseded`：只保留历史，不更新当前状态。

同一物理来源可包含多个角色。角色必须在逻辑数据集层确定。

## 7. 身份与合并

### 身份顺序

1. 权威稳定标识；
2. 已确认内部标识；
3. 标准名称和登记别名；
4. 多属性组合；
5. 人工确认。

### 合并规则

- 事件追加；
- 集合属性去重合并；
- 关系按方向和有效期维护；
- 当前状态按谓词级来源权威性、时间和范围更新；
- 推断仅进入推断区；
- 冲突保留候选值；
- 删除以失效或结束事件表达；
- 人工维护内容与生成内容分区。

Schema 必须定义谓词级权威性，不允许“最新文件覆盖全部字段”。

## 8. 冲突和不确定性

以下情况必须产生质量标记或冲突：

- 主体不明确；
- 多个对象可能匹配；
- 时间或范围缺失；
- 单位、精度、口径不明确；
- 来源内部自相矛盾；
- 多来源对同一时点和范围给出不同值；
- 计算或引用不可复现；
- 视图与证据层无法对账。

不确定性应转化为待核验项或上下文限制，不由 Agent 静默填补。
