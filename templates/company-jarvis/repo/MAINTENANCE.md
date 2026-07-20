# {{COMPANY_NAME}} JARVIS 维护指南

JARVIS 是 {{COMPANY_NAME}} 的路由、索引与综合层。它不镜像原始内容，而是帮助 agents 理解公司、进入正确工作闭环、并保留可复用学习。

---

## 目录职责边界

| 目录 | 存什么 | 不存什么 |
|------|--------|---------|
| `modules/` | 客户业务/产品知识：模块身份、接口、已知问题、决策、被拒需求、测试覆盖 | 完整实现细节、原始 source 代码 |
| `sources/` | 访问路由：identity、access、owner、query、retrieval evidence、redaction、freshness、writeback、status | source 内容镜像、SKILL.md |
| `skills/` | entry skill 的路由收束、workflow skill 的闭环定义/gate/handoff/writeback | source 镜像、repo-local 工程细节 |
| `references/` | 长期跨任务规则：质量门、写回治理、运行治理、路由规则、redaction | 临时笔记、会话上下文 |
| `cross-cutting/` | 模块间交互合约、版本变更索引、同类产品契约对照 | 单模块内部细节 |
| `evals/` | 校准案例、replay registry | 原始日志全文 |
| `_bootstrap/` | 引导证据、pilot 产物 | 已完成闭环的持久知识 |
| `tools/` | 公司 Jarvis 自有高信号可复用辅助工具索引 | jarvis-box install 托管的 capability |

repo 内工程执行真相留在 repo-local skills，不进入 Jarvis。

---

## 维护模型：History → Present → Future

### History（历史学习）

- **数据来源**：pilot 运行记录、history replay 案例、已处理的问题记录
- **证据位置**：`evals/`、`_bootstrap/` 和原始 authority pointer
- **持久位置**：通过写回判断后进入对应 module、source、reference 或 skill
- **关键原则**：不从单次偶发事件提取规则；不对原始日志做全文倾倒

### Present（当前状态）

- **数据来源**：discovery 证据、模块合约、source route contract、运行时状态
- **存储位置**：`modules/`、`sources/`、`cross-cutting/`、`references/`、`jarvis.toml`
- **更新方式**：证据变化时更新对应合约文件；状态变化时更新 jarvis.toml
- **关键原则**：每个事实只有一个 primary home；未确认事实必须写清 `unresolved` / `needs-owner-confirmation` 和所缺证据

### Future（演进方向）

- **数据来源**：acceptance drift 分析（参照 `references/completion-standard.md` 和 `bootstrap-result.json`）、pilot 缺口、owner 确认的方向决策
- **存储位置**：本文件的 rollout 状态段
- **更新方式**：每次 pilot 或 replay 完成后的 calibration
- **关键原则**：方向决策先于实现；不被短期缺口推动做长期结构变更

---

## 维护工作流：START → WORK → VERIFY → END

每次维护按以下四阶段执行：

### START — 触发与 authority

- 明确触发来源（pilot 完成、replay 失败、真实任务反馈、owner 指令、acceptance drift 检测）
- 确认有权修改的目标文件和范围
- 读取 `references/writeback-governance.md` 确定本次属于事实修正还是方法扩展

### WORK — 读取现状，最小更新

- 先读取目标文件和关联的 evidence pointer，理解当前结构和状态
- 只写入本次闭合所需的最小事实或规则
- 区分稳定事实修正与 skill 方法扩展：skill 扩展必须先完成 `no_skill_gap` 判定（见 `references/writeback-governance.md`）
- 不覆盖冲突条目，标记 `writeback-conflict` 进入确认流程

### VERIFY — 链接、证据、行为

- 检查新增或修改的条目是否引用了有效 evidence pointer
- 检查跨文件链接是否仍然有效
- 使用原 replay case、等价真实任务或直接事实检查，证明写入有效

### END — 闭合

- 明确本次维护的闭合结论：`no_skill_gap` / 已写入 primary home / 已建立镜像 pointer / 已标记冲突待确认
- 记录最小决策信息（触发来源、事实/方法、归属、验证结果）

---

## 文件写入契约

### 全局规则

1. **路由，不复制。** source 内容留在 source，不复制进 Jarvis。Jarvis 只维护到达路径和证据指针。
2. **模式优先于日志。** 记录重复出现的模式、约束和路由线索，不做原始时间线记录。
3. **每条事实只有一个归属。** 属于 repo 内的权威来源就路由回 repo，不集中写入 Jarvis。
4. **先读再写。** 追加或改写前先匹配现有结构和约定。
5. **不伪造确定性。** 未确认的信息必须显式记录状态、证据缺口和确认人。

### 每类文件的写契约

| 文件/目录 | 应包含 | 不应包含 |
|---|---|---|
| `modules/<name>/overview.md` | 模块业务目的、边界、首跳路由、first proof、依赖和 evidence pointer | 完整实现细节、原始 source 代码 |
| `modules/<name>/known-issues.md` | 有历史证据的重复故障模式、已验证根因或排查路线 | 原始问题全文、未经验证的猜测 |
| `modules/<name>/decisions.md` | 持久设计决策、取舍上下文、替代方案、后果 | 偶发 bugfix 备注、仍在讨论的提案 |
| `modules/<name>/rejected-features.md` | 被明确拒绝的想法、理由、决策上下文 | 活跃提案、待确认方向 |
| `modules/<name>/test-coverage.md` | 按区域的覆盖情况、缺口追踪 | 逐条测试用例列表 |
| `sources/<name>/README.md` | source route contract：identity、access、owner、query、retrieval evidence、redaction、freshness、writeback、status | source 内容镜像、SKILL.md |
| `cross-cutting/*.md` | 跨模块交互合约、版本变更索引、同类产品契约对照 | 单模块内部细节 |
| `references/*.md` | 持久路由规则、质量门、写回治理、运行治理 | 临时笔记、会话上下文 |
| `skills/<entry>/SKILL.md` | entry skill 的路由和闭环收束 | source 镜像、repo-local 工程细节 |
| `skills/{{COMPANY_SLUG}}-workflow-<name>/SKILL.md` | 闭环工作流定义、gate、handoff、writeback 规则 | repo-local 低层实现 |
| `tools/README.md` | 可复用工具索引 | jarvis-box install 托管的 capability |
| `jarvis.toml` | project、identity、runtime、bootstrap routing pointers | secret、source/repo 事实 |

---

## Pilot 与历史回放校准

```
pilot 运行 → 收集证据 → 对比 oracle → skill-update-decision
                                              ↓
                                     no_skill_gap / 更新 skill / 创建 skill
                                              ↓
                                     history-replay-case（验证改进）
```

- **Pilot 入口**：`_bootstrap/`
- **Replay 入口**：`evals/`（参照 `references/history-replay.md`）
- **边界**：pilot/replay 循环可以产出 repo-local 改进、company entry/module/reference 改进、source-helper 改进、workflow 改进或 upstream method 改进，按 primary home 决定；不只产出 Jarvis skill 改进

### Session Self-Improvement

真实 agent session 中反复出现的操作失败、路由失败或验证缺口，进入 session
self-improvement 检查。先区分一次性任务事实、客户事实修正和可复用的方法缺口；只有
经过证据、`no_skill_gap` 判断和适用的 replay/pilot 验证后，才写回 repo-local、company
Jarvis、workflow skill 或 upstream method。此机制由 jarvis-box 的安装能力托管，company
Jarvis 只保存客户侧的 owner、路由和写回边界。

---

## Primary-Home Promotion

当知识在多个层面都有用时，按 promotion ladder 上升：

1. task-local notes → 留在 task-local
2. repo execution truth → repo-local skills（不进入 Jarvis）
3. cross-repo routing / workflow rules → Jarvis references 或 workflow skill
4. company-neutral method → 脱敏后 upstream 到 create-jarvis-skill 母版

**Promotion 前提**：真实任务、pilot 或 replay 证明这是可复用、可验证的方法缺口；单个高影响事件也必须说明为什么规则可跨任务复用。

---

## 更新触发器

| 事件 | 预期更新 |
|---|---|
| 重复 bug 被诊断或修复 | 更新对应模块的 `known-issues.md` |
| 持久设计决策做出 | 更新对应模块的 `decisions.md` |
| 提案被明确拒绝 | 更新对应模块的 `rejected-features.md` |
| workflow 发生实质变化 | 更新对应 workflow skill |
| 新 source 被确认纳入 scope | 新增或更新 `sources/<name>/README.md` route contract |
| rollout ownership 变化 | 更新本文件的 ownership 表 |
| pilot 或 replay case 失败 | 先归因，再决定事实修正、`no_skill_gap` 或 skill 更新 |
| 内部方法被证明可跨实例复用 | 脱敏后考虑 upstream promotion |
| acceptance drift 被检测到 | 更新 completion-standard 对照并触发新一轮 pilot |

---

## 增量维护基线

当任务为"继续 {{COMPANY_SLUG}}-jarvis 增量维护"时：

1. 从当前 company Jarvis、上次维护记录和各 source authority 找到最近一次已验证的知识锚点；找不到时如实记录。
2. 按每个 source 的实际变化标识，收集锚点之后与客户业务边界、路由或验证有关的变化。
3. 将候选变化路由到事实 owner，排除一次性状态、原始材料复制和已经被现有条目覆盖的内容。
4. 最小更新对应 module、source、cross-cutting、reference 或 skill，并保留 evidence pointer。
5. 完成验证和闭合记录，把本次已验证位置作为下一次维护锚点。

存在两类锚点时分别记录：
- 最近一次显式 knowledge-layer 增量维护基线
- 最近一次 maintenance/runtime mechanism 升级

---

## Ownership

| Area | Primary owner | 职责 |
|---|---|---|
| source route layer | {{COMPANY_OWNER}} | source 访问、认证、route 准确性 |
| module layer | {{COMPANY_OWNER}} | 模块合约、known issues、decisions |
| workflow skills | {{COMPANY_OWNER}} | 闭环定义、gate、handoff |
| maintenance / governance | {{COMPANY_OWNER}} | 本文件、writeback governance、runtime governance |
| evals / replay | {{COMPANY_OWNER}} | replay cases、pilot registry、calibration |

---

## Acceptance Drift

Jarvis 的实际表现与 `references/completion-standard.md`（以及 `bootstrap-result.json`）之间的偏差即为 acceptance drift。检测方式：
- 每次 pilot 完成后对照 completion standard
- 每次 replay case calibration 时评估是否出现新 drift

任何检测到的 drift 必须记录真实影响、owner 和下一步；是否需要新 pilot 由影响和验证合同决定。

---

## Rollout 状态

- **Bootstrap 状态**：见根 `bootstrap-result.json`
- **Shadow pilot**：BOOTSTRAP_REQUIRED
- **History replay**：BOOTSTRAP_REQUIRED
- **Controlled writeback**：BOOTSTRAP_REQUIRED
- **Day-2 operation**：BOOTSTRAP_REQUIRED
- **已知缺口**：BOOTSTRAP_REQUIRED
- **下次 calibration 触发**：BOOTSTRAP_REQUIRED
