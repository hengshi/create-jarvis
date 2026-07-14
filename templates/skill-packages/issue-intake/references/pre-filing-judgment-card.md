# 建单前判断卡片

此卡片把"看起来像问题/需求"与"现在真值得建新 issue"区分开。它不是额外流程——它阻止 intake 把截图、误解、旧问题换标题或弱证据变成新 issue。

## 判断顺序

1. 一句话 claim 已建立。
2. Claim 归一化已先做（reporter 标注不是 disposition）。
3. 先判断是否存在真实行为缺口或真实需求缺口。
4. 仅在 evidence 能映射到具体 module 时，查阅对应 `{{COMPANY_SLUG}}-jarvis/modules/<module>/known-issues.md`、`decisions.md`、`rejected-features.md`。映射不明时模块保持 unknown，按 company routing 继续查。覆盖所有与 claim 有直接证据关联的模块。
5. 判断是否 duplicate / by-design / rejected。不依赖表面关键词。
6. 评估 workaround 是否真能让用户完成目标工作流。
7. 检查证据底线。
8. 以上都没阻塞才走向 `ready-to-file-*`。

## 真实行为缺口

**是**：有证据表明 supported 工作流在明确条件下未交付其已确认契约；先前可用而当前失败也构成回归信号。

**尚不能证明**：只有"感觉不合理"而没有明确期望、实际和契约依据；或当前证据只支持一种尚未验证的操作、配置、数据、权限或实现解释。后者仍可能是产品缺陷，不能仅凭解释类别排除 bug。

## 真实需求缺口

**必须能说清**：谁会用它、什么场景、为什么当前产品不支持此目标、不解决会阻塞什么或替代路径成本为何不可接受、大致验收标准，以及它与 {{PRODUCT_IDENTITY}} 已确认 scope 的关系。

**不是**：只是"稍微方便一点"；个人偏好或参考其他产品口号无法落到场景；已有能力错误却被标为 feature。

## Duplicate 判断

从以下维度评估，而非只看标题像不像：

- 主要行为差异是否与已有 issue 相同
- 触发条件/入口路径是否同类别
- 受影响对象/范围是否同类别
- known-issues 或历史 issue 是否描述相同的 root cause
- 此输入只是新 case/截图/时间戳，还是不同的问题线

**更可能 duplicate**：同一主要问题，不同客户/对象 ID/截图/时间戳。已有 issue 已覆盖主要问题，此输入只是补充证据。

**不应判 duplicate**：表面相似但触发条件/期望实际和影响链不同。已有 issue 只覆盖旁系症状非当前主要问题。

## By-design 判断

需要正面证据（明确的产品边界来源），不能是"没证明是 bug 就是 by-design"。

**更可能 by-design**：`decisions.md` 明确记录这是有意为之的边界/限制/取舍；当前行为与已知规则一致，只有 reporter 期望不同。

**不足以判 by-design**：只有模糊印象无具体 decision 匹配；历史 decision 已过时解释不了实际缺口；在设计边界内应能用的 supported flow 现在坏了——更像 bug。

如果结果符合设计但 reporter 想改变边界，评估是 new feature 还是已被拒绝的方向。

## Rejected-request / Wontfix-history 判断

**更可能 rejected**：`rejected-features.md` 已包含高度相似需求；历史 issue/评审结论已明确声明 rejected/wontfix。

但"之前被拒绝"不意味永远不能重提。只有以下两者均为真才能用历史拒绝阻塞：
1. 当前需求和历史上被拒绝的是同一件事。
2. 当时的拒绝核心原因今天仍然成立。

**值得重新评估的新背景**：新法规/合规/合同需求；从单点变成普遍痛点；产品/架构边界已变旧成本评估不再适用；从低优先级变成关键阻塞。

## Workaround 质量

有 workaround 不意味不应建 issue。真 workaround 必须：目标用户今天能用它完成主要业务目标，走 supported 官方路径，不需要工程/脚本等高成本人工介入，成本可接受。

**不算真 workaround**：只有工程/运维人员才能救场；需反复手动改数据/绕过正常路径；只能拿部分结果主要工作流仍无法完成；技术可行但业务成本高到无法使用。

对判断的影响：workaround 本身是 supported 官方路径且现象被设计边界解释 → 更可能 by-design。workaround 重/脆/成本高 → 不要因此否认真缺口。

## 最低证据阈值

### Bug/Regression 必须
- affected surface / 环境身份（能定位问题所在）
- 复现步骤或观察路径
- 期望 vs 实际
- 足以支持或推翻当前 disposition 的可搜索文本证据（从 claim 原文与 source 可检索字段推导）
- 足以说明优先级和影响的上下文

### Feature/Enhancement 必须
- 目标用户和场景
- 当前痛点
- 目标能力
- 为什么值得做
- 基本验收标准

**仍算证据不足**：只有截图/录屏/聊天转发无文本事实；只有"想要"或"不对"无位置/场景/行为差异。

## 何时输出 blocked-needs-evidence

以下任一适用且 agent 已穷尽当前授权范围内与该判断相关的证据动作时，停止建 issue：
- 尚不能建立真实行为缺口/需求缺口
- 尚不能排除 duplicate/by-design/rejected
- 只有附件无文本事实
- 入口路径/环境身份过于模糊
- 期望或实际缺失
- 需求输入无法说明角色/场景/价值/验收
- 提到了 workaround 但不清是否真 workaround

Blocked 输出必须说明：已知什么、已查过哪些知识区、仍缺哪些关键事实、下一轮最需收集哪项。

## 常见假阳性

- 表面相似判 duplicate → 不同条件/行为差异不要合并
- reporter 不满判 bug → 先确认 supported 行为是否真的坏了
- reporter 想要判 feature → 先用 product contract 或 authority evidence 确认它与 {{PRODUCT_IDENTITY}} scope 的关系
- 历史拒绝永不重提 → 先检查当前环境是否已实质性改变
- 能绕过去就不建 issue → 先检查路径是否 supported、成本是否可接受
- 截图/录屏算充分证据 → 不转文字以后无法搜索
- 感觉像设计判 by-design → 无明确 decision 匹配不够
