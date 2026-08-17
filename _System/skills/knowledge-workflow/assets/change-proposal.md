---
type: change-proposal
proposal_id: <required>
created_at: <required>
source_notes: []
target_scope:
status: <proposed|approved|rejected|applied|superseded>
classification:
access_scope:
reviewer:
reviewed_at:
---

# 目标与范围

# 建议变更

每项变更使用独立条目并记录：

```yaml
change_id: <required>
item_status: <proposed|approved|rejected|applied|superseded>
target_subject: <required>
predicate_or_relation: <required>
old_value:
new_value:
temporal_scope:
applicability_scope:
source_locator: <required>
epistemic_status: <required>
reason: <required>
recommended_action:
item_reviewer:
item_reviewed_at:
application_evidence:
```

批次状态不得替代逐项状态。只有 `approved` 项可以进入应用步骤，应用成功后逐项改为 `applied` 并记录证据。

# 新对象候选

# 冲突与歧义

# 失效或归档建议

# 风险与兼容性

# 审核结论

# 应用记录
