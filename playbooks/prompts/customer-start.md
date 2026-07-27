# 客户开始构建 Jarvis

客户在 jarvis-box/container 准备好的、已经登录的 runtime agent 中只说：

> 请为我们准备 Jarvis 构建。检查当前已授权的代码仓库、文档和工作系统，确认我们选择的 GitHub 或 GitLab 以及 customer-owned company Jarvis repo，写好 Company Jarvis construction 与 Repository learning 两个任务文件，并给我两条可以直接启动它们的命令。只有授权范围、公司身份或远端发布目标确实无法判断时再问我。

这个 Agent 只准备任务，不承担随后数小时或过夜的构建。

准备完成后，客户只会得到一个任务目录和两条命令：

- 一条启动 Company Jarvis construction agent；
- 一条启动 Repository learning agent。

客户不需要理解 Phase、eval loop、history replay、cursor 或内部 verifier。
