---
name: knowledge-workflow
description: 将任意来源材料转换为可追溯来源笔记、经审核知识、受控上下文包和规范产物，并维护它们之间的闭环。用于本项目中的知识摄取、更新建议、查询取数、上下文构建、产物生成、审计校验，以及以 Reader、Schema、Recipe、Validator、Template 或脚本扩展能力；不得把场景、行业、对象类型或执行 Agent 固化进核心工作流。
---

# Knowledge Workflow

先阅读项目根目录 `AGENTS.md`。本 Skill 只负责执行稳定主流程和路由资源，不改变项目不变量。

## 选择模式

- `ingest`：识别来源、逻辑数据集和来源角色，形成来源笔记与规范化知识包。
- `update`：比较来源与现有知识，生成新增、修改、冲突、失效或复核建议。
- `retrieve`：围绕明确目标、范围和时间基准构建最小充分上下文包。
- `compose`：使用 Recipe 将已构建的上下文包转换为受控产物。
- `audit`：检查目录、结构、来源、主体、时间、冲突、消费边界和产物追溯。

一个任务可以依次经过多个模式，但每个阶段必须保持独立产物和责任边界。

## 按需读取资源

- 执行 `ingest`、`update` 或 `audit` 前，读取 [references/knowledge-contract.md](references/knowledge-contract.md)。
- 发生任何读取范围判断或文件写入前，读取 [references/storage-and-consumption.md](references/storage-and-consumption.md)。
- 解释新的来源结构时，读取 [references/reader-contract.md](references/reader-contract.md)。
- 新增或使用对象语义、身份和合并规则时，读取 [references/schema-contract.md](references/schema-contract.md)。
- 执行 `compose` 或新增产物类型时，读取 [references/recipe-contract.md](references/recipe-contract.md)。
- 新增或执行质量规则时，读取 [references/validator-contract.md](references/validator-contract.md)。
- 新增任何能力、自动化、模块或独立 Skill 前，读取 [references/extension-governance.md](references/extension-governance.md)。

只读取当前模式需要的参考文件，不一次性加载全部资源。

## 核心流程

### 1. 确认任务契约

明确：

- 目标和预期产物；
- 授权读取与写入范围；
- 目标对象或主题范围；
- 时间基准和适用范围；
- 权威来源和人工审核要求；
- 可观察完成标准。

关键歧义会改变主体、时间、权限、合并或最终用途时，停止写入并请求澄清。

### 2. 检查当前状态

检查相关目录、已有来源笔记、对象笔记、变更建议、上下文包和产物。优先复用现有标识、Schema、Recipe、Validator、Template 和脚本。

不得因为来源布局不同就假定语义不同，也不得因为名称相同就假定对象相同。

### 3. 识别来源

多份资产作为一个接收批次进入时，先使用 [assets/source-batch.md](assets/source-batch.md) 登记位置、数量、内容指纹、处理状态和例外。来源批次只做库存与完整性登记，不替代后续逻辑数据集来源笔记。

对每个逻辑数据集判断：

- 边界；
- 来源角色；
- 时间和范围；
- 可识别主体；
- 原始值、显示值和可复现结构；
- 缺失、错误、冲突和不确定性。

Reader 的输出必须遵守知识契约。来源角色为 `view` 或 `superseded` 时，不得默认提出当前事实覆盖。

### 4. 形成来源笔记

使用 [assets/source-note.md](assets/source-note.md)。来源笔记按逻辑数据集建立，不机械按物理文件一一对应。

来源笔记应保存稳定解释和证据定位，不承担对象当前视图。首次处理状态应为待审核或已处理，不得伪装成人工核验结果。

### 5. 生成变更建议

使用 [assets/change-proposal.md](assets/change-proposal.md)。逐项表达：目标主体、拟变更谓词、旧值、新值、时间、来源、理由、冲突、风险和建议动作。

默认不直接修改对象笔记。只有授权和确定性规则均明确时，才可应用已批准建议。

### 6. 更新知识

应用已批准建议时：

- 保留旧事实和来源；
- 追加事件；
- 维护关系有效期；
- 只在来源适合、时间更晚且范围一致时更新当前状态；
- 将未解决冲突保留在对象笔记和任务中；
- 保护人工维护章节。

对象使用 [assets/object-note.md](assets/object-note.md)，非对象型稳定知识使用 [assets/topic-note.md](assets/topic-note.md)。

### 7. 构建上下文包

使用 [assets/context-pack.md](assets/context-pack.md)。按以下顺序取数：

1. 精确定位目标和时间范围；
2. 当前有效状态；
3. 直接关系；
4. 与任务相关的历史；
5. 未关闭事项；
6. 适用主题知识；
7. 冲突、缺口、限制和待核验项；
8. 最小充分来源。

不得把完整知识库或完整历史复制进上下文包。

### 8. 生成产物

`compose` 只允许使用已确认 Recipe 和上下文包。产物不得自行补充无来源事实，也不得绕过上下文包重新混合全部来源。

草稿写入 `40-Outputs/drafts/`。内容审核后进入 `reviewed/`，明确批准后进入 `final/`。`reviewed` 和 `final` 产物必须附带 [assets/output-manifest.yaml](assets/output-manifest.yaml)；草稿在需要复现、协作或审核时也应附带。每个受控产物使用独立目录保存 manifest 与交付文件。

### 9. 校验和收尾

执行适用 Validator、确定性脚本和人工检查。至少验证：

- 目录归类；
- 身份去重；
- 主体、时间、范围、来源和信息性质；
- 冲突保留；
- 上下文最小充分；
- Recipe 遵循；
- 关键结论追溯；
- 文档影响。

运行工作区结构校验：

```powershell
python _System/skills/knowledge-workflow/scripts/validate_skill.py
python _System/skills/knowledge-workflow/scripts/validate_workspace.py --root .
python _System/skills/knowledge-workflow/scripts/validate_artifacts.py --root .
```

不得声称未执行的检查已经通过。

## 扩展路由

新增能力时按以下顺序选择：

1. 新来源解释方式：增加 Reader 资源。
2. 新对象语义或合并规则：增加 Schema 资源。
3. 新产物目标：增加 Recipe 和必要 Template。
4. 新确定性检查或转换：增加 Validator 或 Script。
5. 只有满足独立触发、权限、工具、失败模式或上下文边界时，才增加独立 Skill。

具体资源保存在本 Skill 内：`references/reader-*`、`references/schema-*`、`references/recipe-*`、`references/validator-*`、`assets/` 和 `scripts/`。契约文件保留 `*-contract` 命名，不作为具体模块。

不得因新增场景、对象、来源或输出而复制本 Skill。

## 硬性限制

- 不修改 `10-Sources/assets/` 中的原始来源。
- 不把聊天记录或模型记忆作为永久知识。
- 不用推断覆盖来源陈述、核验事实或确定性推导。
- 不静默解决身份、时间、范围或数值冲突。
- 不将视图、汇总或索引当成新的独立事实。
- 不自动执行未授权的外部写入、发送、审批、发布或不可逆操作。
- 不将任务事实写入 `_System/`。
