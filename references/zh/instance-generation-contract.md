# 实例生成契约

使用这份契约来判断：JARVIS 构建 agent 可以直接生成什么、哪些内容必须由人类确认、以及哪些内容只能通过持续使用和 回写 才能真实形成。

## 核心原则

不要把 scaffold 当成 truth 呈现。

每一个生成出来的 artifact 都应该落入以下三类之一：
1. **可以自动安全搭建**
2. **在被视为 truth 之前需要人类确认**
3. **无法在一开始诚实生成，必须从真实工作中涌现**

## Runtime 调用方契约

有些调用方，例如 jarvis-box，会通过 runtime agent 调用这个仓库，而不是把 templates 复制进调用方仓库。在这种模式下，本仓库仍然是方法论 source of truth；调用方只提供输入、目标路径和 runtime 约束。

### 必须归一化的输入

- target home：`JARVIS_TARGET_HOME` 或 `JARVIS_HOME`
- entry skill：`JARVIS_ENTRY_SKILL`，默认 `SKILL.md`
- 公司名称：`JARVIS_COMPANY_NAME`
- 第一条闭环：`JARVIS_FIRST_LOOP`
- GitLab 范围：`GITLAB_HOST`、`GITLAB_PROJECTS`
- source-of-truth notes：`JARVIS_SOURCE_OF_TRUTH`
- owners：`JARVIS_OWNERS`
- 回写策略：`JARVIS_WRITEBACK_STRATEGY`
- 中性 runtime root：如果提供则使用 `JARVIS_BOX_HOME`

### 最小 runtime 输出

runtime 生成的实例必须包含一个有效入口 skill；除非显式提供了其他 `JARVIS_ENTRY_SKILL`，默认位置是 `JARVIS_HOME/SKILL.md`。同时必须包含足够的 bootstrap 产物，让未来 agent 可以继续试点而不必重新发现上下文：

- `README.md`
- `MAINTENANCE.md`
- build brief
- source inventory
- repo inventory
- workflow inventory
- ownership map
- rollout plan
- confirmation checklist
- `bootstrap-state.json`

### 续传与覆盖策略

`bootstrap-state.json` 是 resume anchor。它应该记录：

- 已确认 answers
- 已生成 files
- 因为看起来是用户手写而被保留的 files
- 未解决问题
- 可获得时记录 methodology repo URL 或 commit

resume 时，不要覆盖用户手写文件，除非 human 明确确认。只有明确标记为 scaffold-owned 的生成文件才可以刷新。

### 命名策略

生成给客户的输出不得假设 Hengshi-specific runtime names、paths 或 owners。JARVIS instance 使用客户自己的命名，runtime 路径使用 `JARVIS_HOME`、`JARVIS_TARGET_HOME`、`JARVIS_BOX_HOME` 这类中性变量。

---

## 1. 可以自动安全搭建

这些 产物 通常适合生成为 first-pass 结构：

- JARVIS 根 README skeleton
- MAINTENANCE guide skeleton
- source inventory skeleton
- repo inventory skeleton
- workflow inventory skeleton
- skill backlog
- ownership map 结构
- rollout plan skeleton
- company JARVIS entry skill 骨架
- source skill 骨架
- repo skill 骨架
- workflow skill 骨架
- module overview skeletons
- source README skeletons
- cross-cutting skeletons，例如 module interactions 和 version changelog indexes
- tools index skeleton
- raw export boundary notes

这些都是结构与方法类 产物。生成时应带有明显占位符和明确适配说明。

---

## 2. 需要人类确认

以下项目在有人类 owner 确认之前，不应被当作既定 truth：

- JARVIS 的业务意图
- 需要优先证明的第一条有价值 workflow
- module boundaries
- source names 和 source owners
- repo roles 和 maintainers
- 权威来源 locations
- workflow boundaries 和 交接点
- 安全或合规敏感的 access paths
- ownership assignments
- 回写 destinations
- 当前 rollout 中明确不纳入范围的内容

Agents 可以提出这些项。Humans 应该对其进行 ratify。

---

## 3. 必须从真实使用中涌现

以下项目无法从零诚实生成，应该通过 START → WORK → END 闭环逐步长出来：

- 真实的 known-issue patterns
- 带有 rationale 的真实 decisions
- 真实的 rejected-feature memory
- 有意义的 test coverage summaries
- 值得信赖的 cross-module interaction knowledge
- 持续性的 version-change understanding
- 因重复需求而诞生的有用 operational tools
- 成熟的 repo-local 操作指引
- 成熟的 workflow 证据 与 handoff rules

Agent 可以为这些文件创建占位结构，但不能伪造可信的最终内容。

---

## 4. 生成顺序

### Step 1 — 定义第一条闭环
选择一条真实业务闭环，并给出它的成功信号。

### Step 2 — 按生成边界分类输出
对每个预期 artifact，判断它属于：
- 现在可搭建，
- 需要人类确认，
- 或必须稍后自然形成。

### Step 3 — 只生成可搭建层
创建初始结构，并带上清晰的占位符与契约。

### Step 4 — 让 humans 确认承载 truth 的字段
不要悄悄把业务 truth、ownership 或 operating boundaries 定死。

### Step 5 — 运行真实 试点
让生成出的结构支撑真实工作。

### Step 6 — 只写回可持续复用的学习
提升那些重复出现的 truth，而不是一次性闲聊内容。

---

## 5. 失败模式

### Bad
- 在没有证据时自动生成详细 known issues
- 虚构 owners 或 maintainers
- 根据通用软件常识猜测 workflow stages
- 把占位历史伪装成真实的组织记忆

### Better
- 生成容器
- 明确标记未知项
- 把 truth 路由给 humans 或未来 回写
- 只从实际工作中增长记忆层

---

## 6. 负责任生成器的验收标准

一个负责任的 JARVIS generator：
- [ ] 区分结构与 truth
- [ ] 清楚标记占位符
- [ ] 请求确认承载 truth 的字段
- [ ] 不伪造历史知识
- [ ] 把 回写 作为走向成熟的路径，而不是假装成熟在 setup 时就已存在
