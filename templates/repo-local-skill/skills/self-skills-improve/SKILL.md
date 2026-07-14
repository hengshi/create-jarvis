---
name: self-skills-improve-{{REPO_NAME}}
description: |
  Self-improvement methodology for the {{REPO_NAME}} repo-local skill. Defines
  when and how to grow the skill package — signal is only a candidate, not
  automatic proof of a skill gap. Only real execution + oracle comparison
  supporting a durable/reusable/verifiable gap justifies a skill change.
---

# {{REPO_NAME}} — Self-Improvement

## When to Improve

**signal 只是候选，不自动证明 skill gap。** 只有真实执行 + oracle comparison 支持 durable/reusable/verifiable gap 才改 skill。单个高影响 case 只要证据完整，也可以成立。

repo-local skill 应在以下条件满足时考虑改进：

### 1. Real Task Failure

真实任务已经执行，并有 outcome、验证或 reviewer correction 可与当时实际加载的 skill 行为比较。不能先假定失败由 skill 导致。

### 2. History Replay Case

Phase 12 history replay 产生可复用、可验证的 gap。只有 `executed` replay + oracle comparison 支持 durable gap 才能写回。

### 3. Pilot Observation

pilot 产生了可定位的行为证据和期望结果。只有“感觉不清楚”而没有可复验行为时，先补 eval case，不直接改 skill。

## Decision Order

```
  no_skill_gap check first
    ├── 现有技能充分 → 记录，不写回
    └── 存在 gap →
          ├── durable/reusable/verifiable? → 选择唯一 primary writeback home
          ├── under-specified / ineligible case? → eval-case-gap / defer
          └── 不满足写回条件 → defer
```

优先 `no_skill_gap`。under-specified / ineligible case 只能 `eval-case-gap` / `defer`，不能写 skill。

## Attribution：区分改进归属

每次改进必须归属到唯一 primary writeback home：

| 归属 | 特征 | 动作 |
|------|------|------|
| **task-local** | 一次性任务上下文，不具复用性 | 记录任务笔记，不写回 skill |
| **repo-local** | 可复用、可验证、属于此仓库 | 编辑此 skill package 中的对应文件。记录 eval log。 |
| **workflow** | 跨仓库或团队流程 gap | 创建或更新 workflow skill。从此 repo skill 的 boundaries 引用。 |
| **company jarvis** | 公司级方法或策略 gap | 向 company Jarvis 提交 MR。在此 repo skill 的 boundaries 中备注。 |
| **upstream** | create-jarvis-skill 模板本身的 gap | 向上游提交改进。不在 repo skill 中绕过。 |

mirror 只在另一个层必须新增最小路由/边界指针才能到达 primary home 时使用；不得把 primary 内容复制一份。

## Gap Classification

使用 Phase 12 统一分类：

| Class | Meaning |
|-------|---------|
| `routing_failure` | 技能未能将 agent 路由到正确子 skill 或 reference |
| `truth_failure` | 技能中事实错误或缺失导致判断错误 |
| `boundary_failure` | repo-local 与 company Jarvis 边界不清导致越界或遗漏 |
| `writeback_failure` | 结果未能写回正确位置 |
| `duplication_failure` | 多个技能或文件重复覆盖同一关注点 |
| `bloat_failure` | 技能包含不必要的通用内容 |
| `promotion_failure` | repo-local 事实被错误提升到 company Jarvis |
| `verification_failure` | 验证步骤无法检测实际错误 |
| `no_skill_gap` | 现有技能充分，偏差来自外部因素 |
| `eval-case-gap` | gap 只来自 under-specified / ineligible case |

## What's Forbidden

### 不复制原始制品

不将整个文件、日志或错误消息复制到 skill 中。提取：
- 能防止错误的**规则**。
- 修复问题的**命令**。
- 出错的**信号**。

### 不将 repo-local 事实提升到 company Jarvis

Repo-local 事实留在 repo-local。提升需经 self-improvement 决策门验证为公司级方法 gap，不应在未验证前将 repo-local execution truth 写入 company Jarvis。

### 不过早扩张

- 新子 skill 必须有独立触发条件、清晰边界和不能由现有文件承载的 durable 方法；否则更新现有 primary home。
- 不为填目录、单个 case 的字面细节或没有行为价值的重复说明新增文件。

## Improvement Workflow

### Step 1: Detect Signal

```yaml
signal:
  type: failure | replay | pilot
  source: "<reference>"
  summary: "<one-line description>"
```

### Step 2: no_skill_gap Check First

先判断现有技能是否已覆盖此场景。只有真实 task/pilot 的执行证据或有效 history replay，加上对应 oracle comparison，证明技能存在 durable gap 时才继续。

### Step 3: Classify the Gap

History replay 使用 Phase 12 taxonomy；必须实际执行后才做 skill failure 分类，未执行是 `not-evaluated`。真实 task/pilot 若尚未形成等价的执行与 oracle 证据，只能作为 candidate。

### Step 4: Select Primary Writeback Home

选择唯一 primary writeback home。mirror 只保存到 primary home 的必要路由或边界，不复制规则正文。

### Step 5: Apply the Fix

1. 编辑对应文件。
2. 如果添加新子 skill，更新 `skills/SKILL.md` 路由。
3. 在 company Jarvis 的 skill update decision 中记录变更目标、证据和不写入的内容。
4. 运行 `precheck.sh` 确认 package 合同；它不证明内容正确或产品测试通过。

### Step 6: Verify

1. 用更新后的 skill 重新 replay 同一 case（如适用）。
2. 确认 skill 现在产生正确指导。
3. 如果修复涉及 reference 文件，验证事实来源。

### Step 7: Close the Loop

1. 把 rerun 证据和 oracle comparison 写回原 case 的固定产物。
2. 只有满足同 case 验收时才把 update 标为 verified；否则保持 proposed/deferred 并记录下一步。
