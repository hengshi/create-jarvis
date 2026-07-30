# Real customer-journey evaluation

本仓库不维护模拟 bootstrap、伪造 repo-local skeleton 或复制 runtime 调度能力的 shell harness。
端到端验证从客户的一句话开始，验证四部分建设旅程及 construction/formal-runtime 两个产品边界。

## Construction journey

1. 从没有 create-jarvis checkout、没有客户 repo 的普通 Host workspace 开始；
2. 只发送“请先运行 git clone https://github.com/hengshi/create-jarvis create-jarvis，读取本地 create-jarvis/SKILL.md，然后帮我构建属于我们公司的 Jarvis”；
3. 检查 Agent 是否先 clone 方法仓库并从本地读取，而不是连续 WebFetch GitHub/raw 文件；
4. 检查 Agent 是否先主持资料 intake，而不是扫描 home、Agent 配置、shell 环境、installed skills、无关 repo 或历史残留；
5. 客户随后提供至少两个真实 Git repo、一个授权文档源和 GitHub 或 GitLab 测试 namespace；
6. 检查 Coordinator 是否创建可恢复的 Construction Workspace，而不是旧 lane RUN/progress 文件或机器 phase state；
7. 执行 Part 1，验证 Company template scaffold 及其 customer-owned Git ref，其中包含 unresolved runtime-governance scaffold；
8. 并发或顺序执行 Part 2 与独立 Part 3 cards，检查 Company repo 与每个代码 repo 的 single-writer 边界；
9. 检查 Part 2 是否从客户授权的 Host runtime facts 建设宪法，并安装/验证所需 foundation，或诚实标记 `pending-runtime-foundation`；
10. 为 Part 3 提供隔离 replay，hidden historical outcome 不暴露给 executor，并审查 repo-local diff、same-case before/after 和各 repo 的 Git 交付；
11. 执行 Reconciliation Gate，用真实 artifact 验证 Company → module/source → repo-local handoff；
12. 用真实客户 case 把一个 workflow 推进到 `construction-ready`，确认它没有直接变成 `active`；
13. `scripts/verify_construction_workspace.py` 与 `scripts/verify_company_output.py` 只检查确定性结构、安全和 evidence contract，不替代语义评审。

## Formal runtime journey

1. 只在 Reconciliation Gate 与目标 workflow 的 `construction-ready` evidence 可复验后开始 Part 4；
2. 使用 jarvis-box 项目发布并校验过的 release bundle，以及一个 multi-arch、digest-pinned production image；该 image 内置固定版本的真实 uv-im-connector；
3. 固定 Company Jarvis 与所需 repo-local commits，建立独立高权限正式 identity；
4. 逐项记录 download/checksum/image/start/auth/verify/onboarding work-card checkpoints；
5. 运行容器内 Agent、Git provider、source、workspace read/write 和 Company routing probes；
6. 检查两个 Compose service 是否使用同一 image digest，以及 deployment lock 是否记录准确 commits、单一 image digest、内置 connector version/commit、identity 和 probe evidence；
7. 若 Part 4 回写 Company runtime governance 并改变 commit，重新物化 snapshot 并完整 verify 后才接受最终 lock；
8. 用监督的真实任务推进 `runtime-deployed → ready-for-shadow → shadowing`；
9. 只有代表性任务稳定闭合并得到客户批准后才推进到 `active`；
10. 后续 repo learning 发布新 ref 时，确认当前 active snapshot 不会隐式漂移。

jarvis-box 的 image、Compose、persistence、identity、Company Context Resolver 和 connector 集成测试在
jarvis-box 项目负责。create-jarvis 负责定义跨边界验收并消费已发布的不可变 artifact，不在本仓库
实现第二套 runtime。
