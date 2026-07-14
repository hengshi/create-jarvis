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

## 当前 Skills 是被测对象

- replay 使用运行时当前安装的 company、repo-local、source 和 workflow skills，并在运行开始时记录各 entrypoint/version pointer。
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

1. **skill gap**：现有 guidance 缺少可复用且可验证的方法规则。
2. **实例事实缺口**：company Jarvis 或 repo-local 内容缺少当时本应可取得的必要事实。
3. **source / access / environment**：来源、权限、工具或执行环境阻断了任务。
4. **执行偏差**：当前 guidance 已足够，但 agent 没有遵循。
5. **case 构造缺陷**：visible START 不足、cutoff/provenance 不成立、oracle 不可验证或发生答案泄漏。
6. **历史 outcome 局限**：oracle 本身不是完整或唯一正确解，不能据此判定 skill 失败。

完成归因后再做 `no_skill_gap` 判断。只有第 1 类有充分证据时才进入 skill 写回；其他类别分别修实例事实、source/access/environment、执行过程或 eval case。replay 未实际执行或 oracle comparison 未完成时，只能记录未评估，不能得出 `no_skill_gap` 或 skill gap。

## Writeback 条件

只有满足以下任一条件时才进入 writeback：

- 同一 skill gap 在多个 episode 中复现
- 单个 episode 影响足够高，且 gap 可复用、可写成可验证规则

writeback 时先写入 primary home，再考虑是否需要镜像 pointer。

不设 episode 数量或 case 数量的最低阈值。只要求 case 满足：真实、有足够初始信号、有可验证结果、有授权访问。

## 执行流程

### 1. 搜索并筛选真实 episode

主动扫描已授权的 repo 历史、issue、MR、事故或交付记录。选择 START 与 outcome 可分离、初始信号足以开工且结果可验证的 episode；找不到时记录已扫描范围和缺口，不编造 case。

### 2. 构造 outer case

记录 episode pointer、cutoff、visible fact provenance 和 hidden oracle。逐项解释每条 visible fact 为什么在 cutoff 前可得；无法证明的内容移出 visible START。

### 3. 构造 visible packet

只放初始任务、允许的 source/repo、cutoff snapshot、已知约束和当前 skill entrypoints。对照 oracle 做泄漏检查；不合格时修 case 或更换 episode，不启动 replay。

### 4. 建立隔离环境

使用独立 container、VM 或等价文件系统边界。只挂载 visible packet、允许的 cutoff source snapshot、裁剪后的当前 Jarvis runtime 和独立输出目录。记录 agent CLI、挂载 allowlist、checkout identity 和 skill pointers。

### 5. 执行原任务

replay agent 按当前 skills 完成路由、WORK、VERIFY 和 END。原任务需要修改时应在可写 snapshot 中真实修改并运行可用验证；原任务是分析或评审时，按其原始交付合同执行。

### 6. 由外层 agent 比较 oracle

按上述比较维度对比 replay 产出与 hidden oracle。结果分类：

- `matched`：关键维度正确，行为结果等价或更优
- `partial`：已执行，但关键证据、边界、验证或闭合不完整
- `mismatched`：已执行，但关键路由、事实或行为结果错误
- `blocked`：在形成足够执行证据前被来源、权限、工具或环境阻断
- `invalid`：case 泄漏、START/provenance 不成立或 oracle 不可用于比较

只有外层 agent 可以读取 hidden oracle 并做比较；replay agent 不自评 oracle。

### 7. 归因并判断 no_skill_gap

对所有非 `matched` 结果执行上面的归因。读取实际 skill trace，判断是 skill 缺口、实例事实、环境、执行偏差还是 case/oracle 问题。

### 8. 受控写回与复跑

确认为 skill gap 后，按 `writeback-governance.md` 选择主归属。写入最小可验证规则，再用同一 visible START 复跑；同 case 复跑证明修复了该回归，不单独证明跨 episode 泛化。

### 9. 更新注册表

记录运行 identity、结果、比较、归因、`no_skill_gap`/写回决定、复跑证据和下一步。未执行的维度不得标为通过。

## Case 最小语义

每个 case 至少包含：

- 唯一标识
- 来源 episode 的指针（issue/MR/commit 链接）
- visible START 快照指针
- hidden oracle 指针及其访问边界
- cutoff 时刻和 provenance 说明
- 当前被测 skill pointers，以及该 episode 是否曾影响这些 skills
- 隔离方式和运行证据 pointer
- replay 结果、oracle comparison、归因与写回决定

记录格式为自由文本，不要求固定 YAML/JSON schema。

## 停止条件

单个 case 在以下情况闭合：

- `matched`，且比较与验证证据完整；
- 非通过结果已完成归因，并已修正正确 owner、进入受控写回或记录真实 blocker；
- skill 已更新时，同一 case 已复跑并记录改善或未改善。

以下情况立即停止该 case 的 replay，不产生 skill 结论：

- visible START 含 hidden outcome 或 provenance 无法成立；
- replay agent 可读取 oracle、未来 refs 或已有 failure analysis；
- 没有可验证的历史 outcome；
- 没有授权访问 episode 或执行所需材料；
- agent 未真正执行，或执行轨迹不足以支持比较。
