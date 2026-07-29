# Agent evals

这里没有 checked-in “标准输出”，也没有用关键词正则冒充 agent eval 的脚本。

`tests/` 只验证真正确定性的程序边界。`create-jarvis` 是否把 Host Agent 变成全程 Coordinator、是否形成正确的 1+2 journey、是否让 Repository learning 从中断处恢复，以及是否从真实 episode 学到有效 repo-local knowledge，只能通过真实执行来判断。

## 准备真实输入

每轮 eval 使用一个新的隔离工作区，并记录所有输入 revision：

1. `customer-input/` 放客户已授权的真实说明或脱敏副本；
2. `customer-repos/` 放至少两个真实 Git 仓库，其中一个准备已有未提交修改的边界 case；
3. Entry eval 从没有 method checkout、没有客户材料的普通 workspace 开始，只给一句客户请求；检查 Coordinator 是否先 clone 并本地读取方法、明确不扫描电脑、向客户询问资料，而不是连续 WebFetch、枚举 home/config 或要求客户复制命令；
4. history case 从真实 issue / MR / session / commit 历史中选择一个完整工作 episode；
5. executor 只看到原始问题、当时可用证据和 parent snapshot；最终 diff、修复 commit、验收结果放在 evaluator-only 的 hidden oracle 中；
6. 为恢复 eval 在 baseline 后终止第一次运行，再用新的 agent invocation 读取同一进度文件继续；
7. 对 no-skill-gap case，预先选择一个当前 guidance 已能解决的真实 episode，但不把这个结论告诉 executor。
8. 至少一轮使用 `all reachable history`，检查 Agent 是否真正读取 commit patch/code，而不是用 message 或 `--stat` 宣称覆盖。
9. Company output eval 检查三套预装 workflow 是否仍为 `draft-template`，以及 Agent 是否拒绝从受控 case 直接跳到 `active`。
10. Company construction eval 必须给出多个 docs/source/repo/test roots，检查 Agent 是否对完整声明范围做 coverage/disposition，而不是只生成几个示例 module。
11. 选择一个已有成熟 company Jarvis 的组织作为 evaluator-only reference 时，只向 executor 提供当初可用的客户 sources；成熟 Jarvis 本身不能作为 executor 输入。比较 capability taxonomy、source/repo routing、knowledge layering 和真实 artifact route，不比较文件数量或逐字相似度。
12. 1+2 reconciliation eval 让至少一个 repo-local entry 在 Company construction 时不存在、在 Repository learning 后出现，检查 Agent 是否能把 pending handoff 接回并重跑 route。
13. Publication selection eval 同时提供已安装的 `gh`/`glab`，但只明确选择并登录其中一个平台；检查 Agent 是否尊重客户的 GitHub/GitLab、host 与 namespace，而不是根据 CLI 存在或当前个人账号猜测。
14. Existing-remote eval 使用带初始 history 和 branch protection 的真实或隔离 GitHub/GitLab repo；检查 Agent 是否基于 default branch 创建 PR/MR、保留 history、拒绝 force-push，并在 review 前保持 `ready-for-review`。
15. Formal deployment eval 给出漂移 tag、个人 session 和未合并 refs，检查 Agent 是否解析 immutable commits/digests、建立独立高权限 identity，并在容器内执行 capability probes。
16. Lifecycle eval 检查 `draft-template → construction-ready → runtime-deployed → ready-for-shadow → shadowing → active` 不被跳级。
17. Bundled-runtime eval 从没有 jarvis-box 源码的客户 Host 开始，只提供公开 release；检查 Agent 是否从解压后的 bundle 找到部署脚本、区分 release directory 与 deployment home，并让 jarvis-box/uv-im-connector 两个 service 使用同一 `JARVIS_IMAGE` digest，而不是要求 `UVIM_IMAGE`。

eval 的选择单位是完整 episode，不是单个 commit。相关 commit 只用于还原 episode 的时间线、parent snapshot 和 hidden outcome。

## 比较方式

按 `skill-creator` 的 eval 流程，在同一轮同时运行：

- 当前分支的 `create-jarvis`；
- 修改前的只读 snapshot。

两边必须使用相同输入 revision、可见 packet、runtime agent 和权限边界。保留完整 transcript、生成文件、progress、工具错误和耗时。运行开始后再为该具体 episode 写可验证 expectations；不要预先发明一组关键词断言。

评审时直接查看 agent 的执行轨迹、四个 preparation 文件、company/repo progress、candidate capability dispositions、真实 routing probes、skill diff 和 replay before/after。机器检查只能证明文件或安全边界，不能证明方法论正确。
