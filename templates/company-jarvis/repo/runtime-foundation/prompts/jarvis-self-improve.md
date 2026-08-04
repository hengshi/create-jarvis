# Company Jarvis Self Improve

从最近真实 Agent session 中提炼可复用的方法改进，不要从零生成 Runtime Foundation。

1. 先读取 `jarvis-self-improve-skill`。如果 runtime discovery 找不到它，立即输出 `BLOCKED_METHOD_SKILL_MISSING`，并记录当前 Agent skill root 与 Runtime Foundation doctor 结果；不得退化成自由发挥的复盘 prompt。
2. 只把稳定、重复出现、可验证的经验写入正确 owner 的 skill、测试或文档；不要把单次事故日志直接固化成规则。
3. Company Jarvis 内容回到当前 Company Jarvis 仓库；公共 `create-jarvis` 或 `jarvis-box` 的改进只能通过各自正式贡献流程交付。
4. 不得读取或输出凭据，不得假定 session 一定位于某个产品专属目录。
5. 没有足够证据时输出 `NO_CHANGES`，不要为了产生提交而修改。
6. repo-local skill 候选必须消费其 router 下的六维 depth contract，先运行机械 audit，再隔离执行 same、adjacent/negative 和 forward eval；expected answer 不能进入 task Agent 上下文。
