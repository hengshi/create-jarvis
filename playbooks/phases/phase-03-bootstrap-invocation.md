# Phase 3 - Agent-native bootstrap 启动

目标：让客户在已经登录的 Codex、Claude 或其他 runtime agent 中直接启动或继续 company Jarvis bootstrap，并在任何业务生成前确认运行身份、能力和目录所有权可用。

Phase 3 不接收一份 CLI 表单，也不创建 jarvis-box Target/Task/Run。当前 runtime agent 就是 bootstrap 协调者；`bootstrap-state.json` 是跨 invocation 的恢复依据。

## Owner

| 层 | 必须负责 | 不负责 |
|---|---|---|
| jarvis-box 安装包 / Docker 或 Apple container image | 提供一个可执行的 runtime agent、Git/VCS 客户端、create-jarvis-skill 入口、明确的 runtime/workspace 路径、可选 isolation bridge；让 agent workspace 与输出目录对 selected agent 的有效 UID/GID 可读写 | 收集客户业务表单、替 agent 猜公司拓扑、保存 agent 登录 secret |
| 客户 operator | 完成所选 agent 的一次性登录；确认授权范围、身份冲突和对外写入审批 | 手工搬运 phase handoff、为可探测事实填写长表单、修复产品内部 UID/目录错配 |
| runtime agent + create-jarvis-skill | 探测 live 能力、选择安全默认、读写 state、协调 Phase 3-14 | 用 `sudo`/递归 `chown` 掩盖安装所有权缺陷、宣称未观测能力已预装 |

上表是目标产品合同。当前安装或 image 尚未提供某项能力时，runtime agent 必须报告 exact capability gap 和 owner，不能假装当前版本已经具备。

## 输入

- 用户对 runtime agent 的直接请求；推荐使用 `playbooks/prompts/agent-native-bootstrap.md`。
- create-jarvis-skill 的已安装路径或 checkout。
- 当前 agent 可见的授权 repos/docs/issues/tests/CI，以及可选的公司名或 URL hints。
- runtime/image 已提供的 allowlist env 和 capability facts。
- `JARVIS_WORKSPACE_ROOT`（若 install/image 已声明）指向 selected agent 拥有的 bootstrap workspace；它不能等同于 service-private `JARVIS_RUNTIME_ROOT`。
- 已有 `bootstrap-state.json`、`bootstrap-result.json` 和 company Jarvis worktree（继续执行时）。

## 路径与权限不变量

1. 先记录 selected agent 的有效 UID/GID、当前工作目录，以及候选 runtime root、workspace、target home 的 owner/group/mode。
2. service-private state 可以归 jarvis-box service user；interactive agent 不应直接修改它。bootstrap workspace、customer repo checkout 和 company Jarvis target 必须由 selected agent 的 UID/GID 可读写，jarvis-box 如需读取则通过明确 group/ACL 或受控接口访问。
3. Linux host install 必须创建或修复 agent-owned workspace；container 必须使用 host UID/GID mapping 或等价可写 volume contract。不能依赖 world-writable 目录作为产品方案。
4. 对将要使用的每个父目录执行最小 read/write/execute probe，并在专用临时文件完成后清理。只读 source 单独标注，不要求写权限。
5. 失败时记录 exact path、当前 owner/mode、有效 UID/GID、需要的访问类型和上游 owner。runtime agent 不盲目执行 `sudo`、递归 `chmod` 或 `chown`；这是 jarvis-box install/image 的 provisioning blocker。

## 步骤

1. 定位并读取 create-jarvis-skill 的 `GOAL.md`、`SKILL.md`、`acceptance.md` 和主 checklist。
2. 识别 selected agent 与 live executable；当前会话已成功接收这次请求时可把它作为 prompt probe 证据，不要求再嵌套调用同一个 agent CLI。外部 agent route 才执行额外最小 probe。secret 只记录 available/missing。
3. 读取 runtime allowlist facts，不 dump 全量 env。优先消费 `JARVIS_WORKSPACE_ROOT`；live probe 证明其归 selected agent 使用后，在其下放 bootstrap work。若没有声明，在当前用户拥有的 workspace 下选择可逆的 local-only 目标并记录为 derived；不得退回 service-private runtime root。
4. 执行路径与权限 preflight。任何 first-workflow 所需路径不可读、workspace/target 不可写时停止，不进入业务发现。
5. 探测 Git、provider CLI/API、method repo、source access 和 isolation bridge；把 `observed-ready`、`missing`、`not-required-yet` 分开记录。
6. 如果根目录已有 state/result，先做完整性审计：读取当前产物和用户改动，运行现有产物适用的 verifier，找到最早失效 phase；从该 phase 继续，并把更晚 phase 恢复为 `pending`。旧 `completed` 只是历史声明。
7. 如果没有 state，初始化最小 state/result，然后进入 Phase 4。不要在 Phase 3 扫描客户业务或生成正式 module。
8. 当前 agent 负责后续编排。可用 sub-agent 时自行派发 bounded lane；不可用时在同一任务中顺序执行并通过 state 恢复，不要求客户新开 session 或复制 handoff prompt。

## 输出

- selected agent、认证状态和 method repo pointer；
- runtime capability inventory；
- effective UID/GID 与路径 ownership/read-write probe；
- target/workspace 的 confirmed 或 derived 来源；
- 新建或恢复模式、最早恢复 phase；
- state/result 路径和下一步。

输出中不要求 `task_id`/`run_id`，也不记录 secret value。

## 停止条件

- selected runtime agent 不可执行、未认证或最小 probe 失败。
- create-jarvis-skill 不可读。
- target path 不安全，或 selected agent 对 workspace/target 没有所需读写权限。
- 必需 source 不可读，且缺少取得访问的授权。
- 继续会要求 runtime agent 使用提权命令修补 jarvis-box 安装所有权。
- 恢复会覆盖无法安全合并的用户编辑。

## 进入 Phase 4 的条件

当前 runtime agent 已读取方法、可以持久化 state，且 bootstrap workspace/target 的权限不变量成立。业务输入不要求在 Phase 3 预先填满；Phase 4 先发现，再只确认不可推导的决策。
