# Real runtime evaluation

本仓库不再维护一套模拟 bootstrap、伪造 repo-local skeleton 或复制 runtime 调度能力的 E2E shell harness。

端到端验证直接使用客户支持的 jarvis-box/container 和真实 runtime agent：

1. 在 agent-owned workspace 准备至少两个真实 Git repo 和一个授权文档源；
2. 使用 `evals/evals.json` 的 Preparation case，检查 Agent 是否只生成四文件 handoff；
3. 实际执行 `START-HERE.md` 中的 Company construction 与 Repository learning 两条命令；
4. 检查 Company construction 是否覆盖全部声明 artifact roots、闭合 included capability 的三类证据，并用真实 artifact 验证 routing；
5. 由 runtime 为 Repository learning 提供隔离 replay，hidden outcome 不挂载给 replay agent；
6. 人工审查完整 trajectory、两份 progress、company route、skill diff 和 same-case before/after；
7. 执行 1+2 reconciliation，确认 company → repo-local handoff 可解析；
8. 用 `scripts/verify_company_output.py` 只检查最终 company repo 的确定性结构与安全边界。

jarvis-box/container 自己的安装、UID/GID、agent launcher、background session、heartbeat 和 replay isolation 应在 jarvis-box 项目中做产品集成测试。本 method pack 不为它们维护第二套 shell 实现。
