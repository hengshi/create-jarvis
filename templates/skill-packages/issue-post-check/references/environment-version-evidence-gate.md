# 环境 / 版本证据 Gate

## 何时使用

仅当版本、环境、部署身份会改变 duplicate、fix coverage 或路由时使用。如果以上均不成立，跳过此 gate。

## 核心规则

比较三类独立事实，不做合并推断：

- reporter 声明的版本/环境
- 从当前入口或 source 直接观察到的运行时 identity
- 历史 fix 所适用的 identity（如历史 issue、VCS 变更、commit 声称某版本已修复）

**证据权重**按 provenance（来源可验证性）、与当前入口的直接性、freshness、source authority 综合判断。不设固定数字优先级；冲突时记录为 disputed，以可验证证据为准。

## 检查方法

1. 提取 reporter claim 中的版本/环境声明。
2. 从当前入口直接观察运行时 identity。不能访问入口时不推断；标记为 unknown。
3. 与历史 fix identity 对齐：
   - 只有当前 source 的版本关系规则能明确证明 fix coverage 时，才能据此判断 duplicate 或 fix gap。
   - 无法验证 coverage → 记录 disputed 或 unresolved。
   - 该事实会改变 disposition → 标记 blocked，不以下调置信度替代。
4. 记录证据：`claimed`、`observed`、`evidence_source`、冲突状态、对 disposition 的影响。

## 完成条件

- 只登记当前 source 实际提供的 identity 维度和关系规则。
- 所有比较都能回指到可验证 provenance；版本关系不能由 source 证明时保持 unresolved。
- 共享 artifact 只保留脱敏 evidence pointer，不写入访问凭证或私有参数。
- 无法验证的 identity 会改变 disposition 时，结果为 blocked，并写明恢复所需证据。
