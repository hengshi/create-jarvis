---
title: Writeback 治理
description: 确定 learning signal 是否应持久化、写入何处、以何种方式写入。
---

# 写回治理

写回处理 pilot、history replay 和真实任务产生的学习信号。只有可复用、有证据、可验证且归属明确的内容，才能进入持久知识或 skill；其余内容留在任务记录或等待确认。

稳定事实修正与 skill 规则扩展是两类动作：

- 已验证的客户事实变化，写回拥有该事实的 module、source route 或 repo-local reference。
- 执行方法缺口只有通过 `no_skill_gap` 判断后，才允许扩展 skill。

## no_skill_gap 判定

准备修改任何 skill 前，先回答：

1. 现有指导是否已足够覆盖该场景？
2. 失败是否来自执行偏差（agent 未遵循已有规则）？
3. 失败是否来自证据缺失、权限不足或环境问题？
4. 失败是否来自一次性情况、临时运行状态或当前 case 构造问题？

现有指导已足够，或现有证据能够完整说明失败来自执行偏差、权限、环境、一次性情况或 case 缺陷，且没有暴露新的可复用规则时，结论是 `no_skill_gap`：不修改 skill。不能因为某个环境问题同时暴露了缺失的通用处理规则，就机械地判定 `no_skill_gap`。

skill 更新必须同时满足：

- 存在现有 skill 无法覆盖的可复用缺口
- 有具体证据（任务记录、replay 结果、真实 outcome）支持
- 可以通过未来的独立执行验证该规则是否有效
- 归属明确（知道应写入哪个 primary home）

`no_skill_gap` 只否定 skill 扩展，不阻止把已经验证的稳定事实修正到它的事实 owner；事实修正仍需授权、provenance 和验证。

## 唯一主归属

| 学习内容 | 主归属 |
|---|---|
| 当前任务才需要的观察、一次性状态、未证实假设 | task-local 记录 |
| repo 内命令、路径、架构、测试、本地陷阱 | repo-local skill |
| 客户业务/产品事实、module 边界、跨 repo 路由、owner 映射 | company Jarvis module / reference |
| 某个 source 的访问、检索、引用、新鲜度和脱敏边界 | source skill |
| 跨 source、repo 或角色的 START -> WORK -> VERIFY -> END 闭环 | workflow skill |
| 任意公司都需要的 bootstrap 阶段、产物和校准方法 | `create-jarvis-skill` |

同一学习如果包含不同 owner 的内容，先拆成多条学习，每条只有一个主归属。

## 镜像写回

仅当另一层必须发现或执行该规则时才建立镜像 writeback。镜像只包含简短 pointer 指向 primary home，禁止复制全文。

## 冲突处理

当新 learning 与已有条目矛盾时：

- 不覆盖现有条目
- 同时保留冲突双方的证据和 authority
- 标记为 `writeback-conflict`，进入确认流程

## Runtime Agent 执行步骤

runtime agent 按以下步骤执行：

### 1. 固定学习信号

记录触发任务或 replay、观察到的行为、证据 pointer、影响和当前不确定项。没有证据的猜测只留在 task-local。

### 2. 区分事实与方法

- 如果只是已验证的稳定事实新增或修正，路由到事实 owner。
- 如果准备改变“agent 以后应怎样做”，继续执行 `no_skill_gap` 判断。

### 3. 判断 no_skill_gap

读取当前已有 guidance，并对照本次真实执行轨迹。现有规则已足够或失败没有暴露可复用方法缺口时，记录 `no_skill_gap`，停止 skill 更新。

### 4. 确定主归属

```
学习涉及特定 repo 的命令/路径/架构/测试/本地陷阱？
  → repo-local skill
学习涉及客户业务事实、module 边界、跨 repo 路由或 owner 映射？
  -> company Jarvis module / reference
学习涉及 source 访问/新鲜度/查询/脱敏？
  -> source skill
学习涉及跨 source/repo 的闭环编排？
  -> workflow skill
学习涉及公司中立的 bootstrap 方法？
  -> create-jarvis-skill
学习只对当前任务成立，或仍是未证实猜测？
  -> task-local，不进入持久 skill
```

若学习可分解到多个 primary home，分别写入各 home。

若无法确定归属，记录 `needs-owner-confirmation` 并升级。

### 5. 检查冲突

写入前读取目标位置。新旧内容冲突时不覆盖，保留双方证据和 authority，标记 `writeback-conflict`，交给有权 owner 确认。

### 6. 最小写入并验证

只写能够闭合本次缺口的最小规则或事实；保留 provenance 和验证方式。使用原 replay case、等价真实任务或直接事实检查，证明写入有效。

### 7. 检查镜像

对每个已确定的 primary home，检查是否有另一层必须发现或执行该规则。若有，在目标层建立简短 pointer，不复制全文。

## 最小决策记录

每次 writeback 决策记录以下信息（自由文本，不要求固定格式）：

- 触发来源（任务 ID / replay case ID / pilot 标识）
- 学习是事实修正还是方法缺口
- `no_skill_gap` 判断及证据
- primary home 及写入位置
- 镜像 writeback 目标（如有）
- 冲突标记（如有）
- 写入后的验证结果或未执行原因
