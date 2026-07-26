---
title: 历史回放
description: 从真实历史 episode 中校准 company Jarvis 和 repo-local skills 的方法。
---

# 历史回放

历史回放从真实历史 episode 构造可重复的 eval case，用当时可见的初始信号重放当前 skills。它用真实结果发现失败模式，但不把历史最终答案当成唯一正确 patch，也不因一次失败直接扩展 skill。

## Episode 定义

Episode 是从真实历史中选取的一个事件，来源可以是 commit、issue、MR、事故记录或交付记录。选取条件：

- 事件发生时存在明确的工作目标
- 事件后来有能够检查的实际结果
- 事件的初始信号（当时可见的信息）足以让执行者开始工作

## 时间切片构造

每个 episode 构造两个时间切片：

**visible START**：仅包含 cutoff 时执行者已经可见，或按照当时授权可主动取得的信号。可以包括：

- 当时已存在的 issue/MR 描述和评论
- 当时已合并的代码和文档
- 当时可访问的 source 和配置
- 当时已经生效的任务约束和客户政策

**hidden oracle**：包含 cutoff 之后才出现的信息：

- 后续 commits、diffs 和最终 patch
- 后续讨论、review correction、根因分析
- 验证结果和最终 outcome（关闭/合并/拒绝/替代方案）
- 事后才能访问的数据和上下文

必须记录 cutoff、每条 visible fact 的 provenance 及其为何在 cutoff 前可见。由最终结果倒推的根因、文件、方法或修复方向不能伪装成初始信号。

## 当前 Calibration Skills 是被测对象

- 第一组从 authoritative company、repo-local、source 和 workflow skills 派生 writable calibration snapshot；之后每组使用上一组闭合后持久化的累计 `calibration_skill_ref`。
- 每次运行记录实际 entrypoint/version pointer、baseline before/after 和 ordered verified candidate set；checkpoint 后不得退回旧 authoritative baseline。
- 历史 checkout/source snapshot 冻结在 cutoff；skills 不回退到历史版本。
- 构造者必须检查当前 skill 是否直接包含该 episode 的 case-specific hidden outcome。若包含，保留该 case 做更新后的回归验证可以，但不能把它当作发现新缺口或证明跨 episode 泛化的独立证据。
- 从其他 episode 提炼出的通用规则可以参与当前 replay；这是检验复用价值的一部分。

## 防泄漏

- 执行 replay 的 runtime agent 不能读取 hidden oracle
- agent 不能访问未来 commit/diff、未来评论
- case 文件命名、目录名和 prompt 不能暗示答案
- case 构建与 replay 执行必须处于独立的可读边界：构建者可以访问 oracle，replay agent 只能访问 visible packet、允许的 cutoff snapshot 和当前 skills
- outer case、oracle、未来 Git refs、bootstrap transcript 和已有 failure analysis 不得出现在 replay agent 的挂载或可读目录中

## Replay 执行

重放的是当时的**任务**，不是让 agent 猜最终 patch。agent 应：

1. 冻结并记录当前被测 skills
2. 在隔离的 checkout 或 source snapshot 上执行
3. 完成路由 → 证据收集 → 方案/修改（适用时）→ 验证 → closure
4. 产出自己的变更或结论、执行轨迹、验证证据和闭合结果

## Oracle 比较

比较 replay 产出与 hidden oracle 时，不要求逐字或逐 patch 相同。比较维度：

- owner 和 route 是否正确
- 关键证据是否被识别和收集
- 行为结果是否等价或更优
- 验证是否充分
- 是否越权或产生幻觉
- 是否有效闭合（closure）

允许更好的等价解。若 replay 产出与 oracle 不同但等价且正确，视为通过。

历史 outcome 是比较证据，不天然是最佳实现。oracle 有错误、遗漏或当时受限时，应如实记录，不强迫 replay 复刻它。

## 非通过结果归因

replay 失败时，先归因再决定是否修改 skill：

1. `skill_gap`：现有 guidance 缺少可复用且可验证的方法规则。
2. `instance_fact_gap`：company Jarvis 或 repo-local 内容缺少当时本应可取得的必要事实。
3. `source_access_environment`：来源、权限、工具或执行环境阻断了任务。
4. `execution_deviation`：当前 guidance 已足够，但 agent 没有遵循。
5. `case_construction_leak`：visible START 不足、cutoff/provenance 不成立或发生答案泄漏。
6. `oracle_limitation`：历史 outcome 不完整或不是唯一正确解，不能据此判定 skill 失败。

完成归因后再做 `no_skill_gap` 判断。只有 `skill_gap` 有充分证据时才形成 skill candidate；其他类别分别修稳定实例事实、source/access/environment、执行过程或 eval case。replay 未实际执行或 oracle comparison 未完成时，Primary 只能 `not-evaluated`、Decision 只能 `defer`，不能得出 `no_skill_gap` 或 `skill_gap`。

## Writeback 条件

只有满足以下任一条件时才进入 writeback：

- 同一 skill gap 在多个 episode 中复现
- 单个 episode 影响足够高，且 gap 可复用、可写成可验证规则

Phase 12 只在 writable calibration snapshot 形成 candidate、完成同 case 验证并累计；Phase 13 才按 primary home 的政策应用到 authoritative home，再考虑是否需要镜像 pointer。

不设 episode 数量或 case 数量的最低阈值。只要求 case 满足：真实、有足够初始信号、有可验证结果、有授权访问。

## 按 Commit 组的执行流程

### 1. 建立轻量 cursor

先声明 `seed` 或 `full-range` mode，并记录 repo、请求边界、方向、owner、resume entry、`next_commit`、当前 `calibration_skill_ref`。不要先把整个时间范围分类。

### 2. 扩成最小相关组

从 cursor seed 立即依据同一 issue/MR key、连续主题、高信号文件重叠、follow-up cleanup 和补充 tests/verification 扩组。记录 `group_commits`、cursor before/after 与非 seed 的 `preconsumed_commits`；跨非连续提交扩组时 cursor after 仍按 seed 的遍历顺序推进，preconsumed 成员只在以后 encounter 时跳过。refactor/tests/docs/release/noise 随 cursor encounter-and-skip，或并入其服务的 bugfix/feature 组。

### 3. 构造 outer case 和 visible packet

从组内最早 parent 与独立 pre-fix artifact 构造 visible START，记录 provenance 和 hidden oracle。完整 final subject、diff、changed paths、cause、fix、最终测试都属于 oracle；只有纯外部症状可谨慎标为 `reconstructed-from-outcome-subject` 投影。visible packet 只含初始任务、允许 source/repo、cutoff snapshot、约束和当前 calibration skill entrypoints。

### 4. 建立隔离环境并执行原任务

使用独立 container/VM 文件系统边界，只挂载 visible packet、cutoff source snapshot、裁剪后的当前 calibration runtime 和独立输出。replay agent 按实际 skills 完成路由、WORK、VERIFY 和 END；需要修改时在可写 cutoff snapshot 中真实修改和验证。

### 5. 由外层 agent 比较 oracle

outer coordinator 先读取 exact replay result 和完整 hidden oracle，再比较 route/owner、关键证据、fix boundary、行为结果、验证和 closure。结果为 `matched`、`partial`、`mismatched`、`blocked` 或 `invalid`；replay agent 不自评 oracle。

### 6. Primary attribution 与 candidate

先用上述精确枚举归因。只有 `skill_gap` 才调用 `skill-creator` 修改实际 primary skill home 的候选副本；`instance_fact_gap` 只有当前权威来源可独立证明稳定事实时，才形成最小 fact-correction candidate。其他 attribution 记录 no-update/defer。不得创建 eval-loop skill，也不得把单个 commit 的答案写进 skill。

### 7. Same-case rerun 与累计 baseline

保持同一 START、cutoff、allowed sources 和 oracle 复跑 candidate。只有失败维度改善、正确维度无回归且验证成立才标 verified。verified skill/stable-fact candidate 先晋升为累计 calibration baseline，保存 baseline before/after、新 `calibration_skill_ref` 与 ordered candidate set；`no_skill_gap`/defer 保持 ref 不变。

### 8. 持久化状态并关闭组

保存 case、comparison、decision、candidate diff/rerun 和 cursor before/after。先持久化累计 ref，再推进 cursor。full-range 到请求边界前保持 `in-progress`；seed 可在至少一个有效组闭合后，把剩余范围连同 cursor/ref、owner 和 resume entry 交给 day-2，但不得宣称全范围完成。

### 9. Phase 13 受控应用

到达当前 scope completion boundary 后，Phase 13 按 ordered candidate set 应用到 authoritative primary homes，核对最终 authoritative ref 与累计 baseline 等价，并用最终累计 authoritative snapshot 复跑所有受影响 case，防止后续 candidate 让早期 case 回归。

## Case 最小语义

每个 case 至少包含：

- 唯一标识
- 来源 episode 的指针（issue/MR/commit 链接）
- group commits、cursor before/after、preconsumed commits
- visible START 快照指针
- hidden oracle 指针及其访问边界
- cutoff 时刻和 provenance 说明
- 当前被测 skill pointers、calibration ref before/after，以及该 episode 是否曾影响这些 skills
- 隔离方式和运行证据 pointer
- replay 结果、oracle comparison、归因与写回决定

产物可以是 Markdown，但必须完整实例化 create-jarvis-skill 的 canonical `history-replay-case.md`、`replay-failure-analysis.md`、`skill-update-decision.md` sections/fields，并按 `replay-case-registry.md` 维护 cursor；不得用缩减自由文本替代执行合同。

## 停止条件

单个 case 在以下情况闭合：

- `matched`，且比较与验证证据完整；
- 非通过结果已完成归因，并已修正正确 owner、进入受控写回或记录真实 blocker；
- candidate 存在时，同一 case 已复跑；verified candidate 已进入累计 baseline并持久化新 ref。

以下情况立即停止该 case 的 replay，不产生 skill 结论：

- visible START 含 hidden outcome 或 provenance 无法成立；
- replay agent 可读取 oracle、未来 refs 或已有 failure analysis；
- 没有可验证的历史 outcome；
- 没有授权访问 episode 或执行所需材料；
- agent 未真正执行，或执行轨迹不足以支持比较。
