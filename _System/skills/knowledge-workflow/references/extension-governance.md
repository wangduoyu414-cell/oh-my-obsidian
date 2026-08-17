# 扩展治理

## 目录

1. 复用顺序
2. 扩展路由
3. 独立 Skill 门槛
4. 基础设施升级门槛
5. 扩展提案
6. 兼容和文档
7. 物理组织与命名

## 1. 复用顺序

新增实现前按顺序检查：

1. 现有行为、配置或人工流程是否已满足；
2. 现有 Reader、Schema、Recipe、Validator、Template 或 Script 是否可复用；
3. 标准库、平台或运行环境能力是否足够；
4. 已安装依赖是否合适；
5. 最小直接实现是否足够；
6. 最后才增加新模块、依赖、服务或 Skill。

在最早能够完整满足要求的层级停止。

## 2. 扩展路由

| 缺口 | 扩展位置 |
|---|---|
| 无法解释新的来源结构 | Reader |
| 无法表达新的身份、谓词、关系或合并规则 | Schema |
| 无法定义新的产物目标和验收 | Recipe |
| 无法稳定检查新的确定性质量要求 | Validator |
| 缺少重复使用的表现形式 | Template |
| 重复、易错、需复现的机械过程 | Script |
| 项目不变量或责任边界改变 | AGENTS.md |
| 工作流模式或资源路由改变 | SKILL.md |

新增场景不等于新增架构层。先将变化映射到上述资源。

## 3. 独立 Skill 门槛

独立 Skill 至少需要一个清晰边界：

- 独立触发语义；
- 独立权限或敏感性；
- 独立工具、服务或运行环境；
- 大量专属上下文，继续放入核心 Skill 会影响其他任务；
- 独立失败、恢复、验证或生命周期。

新来源、新对象、新产物、新组织范围或新措辞本身不能证明需要新 Skill。

独立 Skill 应复用本项目知识契约和存储契约，不创建平行知识库或不同事实模型。

## 4. 基础设施升级门槛

只有出现可观察证据时才升级：

- 当前检索无法满足召回或响应要求；
- 当前存储无法满足并发、权限、事务或审计要求；
- 当前执行无法满足稳定性、恢复或吞吐要求；
- 当前手工审核成本已成为确认瓶颈；
- 已有规模或故障记录证明简单方案不足。

升级前必须保留：来源权威性、统一知识契约、对象稳定标识、变更建议、上下文包和产物追溯。基础设施不得成为新的事实来源。

## 5. 扩展提案

扩展提案至少包含：

```yaml
objective:
observable_acceptance:
current_gap:
evidence_of_gap:
reuse_options_considered: []
chosen_boundary:
affected_contracts: []
affected_consumers: []
permissions_and_risks: []
failure_and_recovery:
validation_plan:
maintenance_cost:
rollback_plan:
```

缺少真实缺口证据、验收方法或责任边界时，不实施。

## 6. 兼容和文档

- 优先向后兼容；破坏性变更必须有迁移和回滚方案。
- Schema 版本变化要说明对象迁移。
- Recipe 变化要说明产物兼容性。
- Validator 变化不得通过降低标准适配错误实现。
- 路径和术语变化要同步 `AGENTS.md`、`SKILL.md`、引用和校验脚本。
- 完成后用代表性真实任务验证，而不是只检查文件是否存在。

## 7. 物理组织与命名

具体扩展资源与核心 Skill 一同分发，并使用以下路径：

- `references/reader-<name>.md`：具体 Reader；
- `references/schema-<name>.yaml` 或 `.md`：具体 Schema；
- `references/recipe-<name>.yaml` 或 `.md`：具体 Recipe；
- `references/validator-<name>.md`：具体 Validator 说明；
- `assets/<name>.*`：可复制或用于交付的 Template；
- `scripts/<verb>-<object>.*`：确定性实现。

`<name>` 使用小写 kebab-case。契约文件使用 `*-contract`，不得被当作具体模块。每个具体资源应声明名称、版本、目标、触发或适用条件、输入、输出、失败边界、验证方式和兼容性。若资源数量增长到影响发现，再增加机器可读索引；在此之前不维护重复注册表。
