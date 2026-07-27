# Real customer-journey evaluation

本仓库不维护模拟 bootstrap、伪造 repo-local skeleton 或复制 runtime 调度能力的 shell harness。
端到端验证从客户的一句话开始，并穿过两个真实产品边界。

## Construction journey

1. 在 Host Agent 可访问的 workspace 准备至少两个真实 Git repo、一个授权文档源和 GitHub 或 GitLab 测试 namespace；
2. 只发送“阅读 create-jarvis 并帮我构建属于我们公司的 Jarvis”；
3. 检查 Coordinator 是否自行准备、派发、恢复 Company construction 与 Repository learning，而不是要求客户运行命令；
4. 检查 Company construction 是否覆盖声明 artifact roots、闭合 capability 证据并发布可消费 Git ref；
5. 为 Repository learning 提供隔离 replay，hidden historical outcome 不暴露给 executor；
6. 人工审查 trajectory、progress、company route、repo-local diff、same-case before/after 和各 repo 的 Git 交付；
7. 执行 reconciliation，并用真实 artifact 验证 company → repo-local handoff；
8. 用真实客户 case 把一个 workflow 推进到 `construction-ready`，确认它没有直接变成 `active`；
9. `scripts/verify_company_output.py` 只检查确定性的结构与安全边界，不替代语义评审。

## Formal runtime journey

1. 使用 jarvis-box 项目发布的 multi-arch、digest-pinned production image 和一个真实 connector image；
2. 固定 Company Jarvis 与所需 repo-local commits，建立独立高权限正式 identity；
3. 运行容器内 Agent、Git provider、source、workspace read/write 和 Company routing probes；
4. 检查 deployment lock 是否记录准确 commits、digests、identity 和 probe evidence；
5. 用监督的真实任务推进 `runtime-deployed → ready-for-shadow → shadowing`；
6. 只有代表性任务稳定闭合并得到客户批准后才推进到 `active`；
7. 后续 repo learning 发布新 ref 时，确认当前 active snapshot 不会隐式漂移。

jarvis-box 的 image、Compose、persistence、identity、Company Context Resolver 和 connector 集成测试在
jarvis-box 项目负责。create-jarvis 负责定义跨边界验收并消费已发布的不可变 artifact，不在本仓库
实现第二套 runtime。
