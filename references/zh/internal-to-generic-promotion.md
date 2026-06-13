# 内部经验到通用方法论的提升

当你判断某个公司 JARVIS 实例中的经验是否应该更新 create-jarvis-skill 时，使用这份参考。

## Promotion ladder

1. Task-local note：只对当前任务有用。
2. Repo-local skill/reference：某个 repo 或 project 的执行真相。
3. Central JARVIS instance：routing、workflow、ownership 或 durable company pattern。
4. Generic create-jarvis-skill methodology：与公司无关、能帮助未来 JARVIS builder 的规则。

不要因为一个经验重要就跳级。

## 放在哪里

Repo-local：
- commands；
- validation；
- local architecture；
- repo-specific failure patterns；
- safe mutation/writeback paths。

Central JARVIS：
- cross-repo routing；
- workflow orchestration；
- source map；
- ownership；
- durable failure patterns；
- writeback/maintenance rules。

Generic create-jarvis-skill：
- company-neutral methodology；
- scaffold contracts；
- pilot design；
- layer boundaries；
- calibration and promotion rules；
- 无私有例子的 reusable anti-patterns。

mirror writeback 是可选项。先为 method change 选一个 primary home；只有另一层必须消费或执行该 contract 时才 mirror。例如，通用 bootstrap result contract 属于本仓库，而消费它的 runtime 可能只需要一个本地 test 或 runbook note。

## Upstream gate

只有同时满足以下条件，才提升到 create-jarvis-skill：
- lesson 不依赖具体公司事实；
- 私有 names、paths、issue IDs、customers、owners、secrets 已移除；
- 可复用于多个 instances 或 companies；
- 改变的是 method，而不只是 fact；
- 有真实使用或 replay 证据；
- 不重复已有规则。
