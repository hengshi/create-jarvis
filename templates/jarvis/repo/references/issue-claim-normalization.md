---
title: Issue Claim Normalization
description: 将 reporter 原始说法归一化为 evidence-backed normalized claim，供 intake / post-check disposition 使用。
---

# Issue Claim Normalization

## 目标与边界

把 reporter 原始描述转成 **evidence-backed normalized claim**，供后续 intake 或 post-check 做 disposition 决策。

本阶段 **不做** 以下判断：duplicate / by-design / rejected、execution owner、root cause。这些是 disposition 或后续工作流的职责。

## 输入

按适用性记录，不设固定维度数：

- `reporter_labeled_type` — reporter 自行标注的类型（如有）
- `observed_behavior` 或 `desired_outcome` — 至少其一
- `expected_contract` 及其来源 — reporter 认为应当成立的行为契约及出处
- `context_identity` — 当前 {{JARVIS_NAME}} source 中会影响路由或复现的上下文身份
- `impact` — reporter 声述的影响
- `evidence_pointers` — 已有证据在授权 source 中的可追溯定位
- `unknown_or_assumptions` — 当前未知或暂按假设处理的部分

维度不适用则不留，不填 `N/A`。

## 双视角判断

### Product / Contract Lens

从产品契约角度审视：user goal 是什么、是否落在已确认的 {{JARVIS_PURPOSE}} scope 内、现有 contract 如何表述。

### Execution / Evidence Lens

从可验证性角度审视：哪些 source 能验证、当前证据支持什么、缺什么。

**视角冲突时**：记录冲突内容、各自 evidence 和能够消解冲突的下一项 proof；在消解前状态为 blocked。

## Normalized Claim Types

每个 issue 归一为以下六种之一：

### 1. `supported-contract defect hypothesis`

存在 supported contract（文档、规格、既有行为契约），且观察到与 contract 不一致的行为。

**门槛**：
- 有 observed behavior 和 expected behavior 的明确对照
- 有 supported contract evidence 指向具体契约
- 有可观察的 evidence（不要求已复现，但必须可观察）

### 2. `product-scope capability gap`

user goal 在已确认的 product scope 内，但当前 contract 未覆盖该能力。

**门槛**：
- user goal 明确
- 当前 contract 可证明不覆盖
- gap 描述具体
- 有 product-scope authority 确认 scope 内
- acceptance criteria 可表述

### 3. `expectation-contract mismatch`

reporter 的 expected contract 与现有 contract 不一致，但现有 contract 本身成立且无 defect。

**门槛**：
- 现有 contract 正面解释了当前行为
- reporter 的 expected contract 可明确表述
- observed behavior 与现有 contract 一致，且当前 evidence 未形成 defect hypothesis

### 4. `request-outside-confirmed-scope`

reporter 诉求落在已确认 product scope 之外。

**门槛**：
- 有 authority / contract 正面证据表明该诉求不在 scope 内
- 区分于 capability gap：gap 在 scope 内但未实现，outside-scope 根本不在 scope 内

### 5. `information-or-usage question`

当前目标是获取信息或使用说明，且尚无 defect 或 gap 的 evidence。仍需由 intake 路由；该类型本身不代表关闭。

**门槛**：
- user goal 是获取信息、解释或使用指引
- 没有足以构成 defect hypothesis 或 capability gap 的 evidence

### 6. `blocked-needs-evidence`

缺失关键事实，且缺失的事实会改变 claim type 判定。

**门槛**：
- 明确列出缺失什么事实
- 说明该事实为何会改变类型判定（而非泛泛"信息不足"）

## 关键约束

- **Reporter label、实现建议、标题是输入，不是事实。** 类型由 evidence 决定，不由 reporter 措辞决定。
- **类型可随新 evidence 变更。** 记录 previous type、new type 和促成变更的 evidence reason。
- **duplicate 是历史关系，by-design / rejected 是 disposition。** 三者均不能作为 normalized claim type。
- **Proof 范围由当前 claim 和 source contract 决定。** 只采集会支持、推翻或区分候选类型的证据。
