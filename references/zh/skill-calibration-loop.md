# Skill 校准闭环

真实工作、pilot run 或历史 replay 暴露失败后，使用这份参考。

## 闭环

```text
real task or historical artifact
-> eval case
-> agent replay
-> failure mode
-> no_skill_gap or scoped update
-> verification
-> repo-local / central / upstream promotion decision
```

## Eval case 来源

好的 eval case 来自：
- 真实 START -> WORK -> END；
- 历史 issue/MR/commit/task outcome 的脱敏摘要；
- owner corrections；
- routing mistakes；
- access/source interpretation failures；
- writeback misses；
- 证明“不能诚实 scaffold”的反例。

一次性 surprise 通常留在 task notes。重复失败或高影响失败才可能推动 skill change。

## Failure taxonomy

| Failure | 含义 |
|---|---|
| `routing_failure` | 进错 module/source/repo/workflow/next hop |
| `truth_failure` | 未确认信息被当成事实 |
| `boundary_failure` | repo-local truth 被中央化，或 central routing 被散落 |
| `route_invalidation` | 后续证据推翻了早期合理 route |
| `writeback_failure` | durable learning 没写或写错位置 |
| `duplication_failure` | 新建 skill 而不是改已有 skill |
| `bloat_failure` | 没有重复价值的 skill/template 膨胀 |
| `promotion_failure` | 私有公司材料被提升为通用方法 |
| `verification_failure` | 结论缺证据或 replay |
| `no_skill_gap` | 现有 skills 足够；失败来自 task/data/runtime/code 层 |

## Calibration discipline

改 skill 前先区分：
- 本次 run 缺 prompt/task evidence；
- source data 或 runtime behavior 超出 skill 控制；
- route 在旧证据下合理，但被后续证据推翻；
- 可重复的方法缺口，且最适合落入稳定 skill 或 reference。

通常只有最后一类才应修改 skill。`route_invalidation` 可能需要加强 route-confidence checks，但不自动说明旧 skill 是错的。

## `no_skill_gap` 门槛

创建或扩展 skill 前先判断 `no_skill_gap`。只有失败可重复、可迁移，并且最适合由稳定 procedural guidance 解决时，才更新 skill。
