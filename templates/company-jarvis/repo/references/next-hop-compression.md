---
title: 下跳压缩
description: 向下一跳只传递继续闭环所需且有 provenance 的事实。
---

# 下跳压缩

## 核心规则

Handoff 只传下游继续闭环所需且有 provenance 的事实。不传 raw dump，也不丢弃关键不确定性。

## Packet 内容

按当前任务适用性选取，不要求每项都填：

- **Original artifact pointer**：原始输入的引用位置
- **Goal / claim**：当前 hop 要解决/验证的目标
- **已验证事实**：本 hop 确认的事实及 provenance
- **被推翻假设**：本 hop 排除的假设及排除依据
- **Unresolved**：本 hop 无法裁定、需下游处理的不确定性
- **Evidence pointers**：支撑以上各项的证据位置
- **为何选择此 next hop**：路由依据
- **期望 next action**：下游应执行的下一步
- **Stop / return condition**：何时停止、返回 routing
- **权限 / 敏感边界**：下游需注意的访问或信息边界

## 独立复核

下游按风险和自身 contract 决定是否独立复核上游结论。复核结果与上游冲突时，带新 evidence 返回 routing 重新裁定。

## 完成标准

Next hop 无需读完整上游线程即可开始工作，但能回溯每个 material claim 到其 provenance。

## Packet 边界

- 压缩格式由当前任务和 next-hop contract 决定，以可执行、可回溯为标准。
- 原始 source 内容保留在 source，只传必要的脱敏事实和 evidence pointer。
- 关键 unresolved、权限边界和被推翻假设不能为了缩短文本而省略。
