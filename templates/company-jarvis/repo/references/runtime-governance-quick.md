# 运行时治理速查

**状态**：强制边界 | **版本**：2.0

本文件先区分执行上下文，再决定是否需要 runtime 检查。Company Jarvis 同时服务建设期和正式
运行期；不能把 jarvis-box 当成所有会话的前置条件。

## 先判定上下文

| 上下文 | 权威事实 | 行为 |
|---|---|---|
| Construction / onboarding | 外部 `BUILD-CONTEXT.md`、`CONSTRUCTION-JOURNAL.md`、当前授权 checkout 与 Git facts | 不要求 jarvis-box；按建设授权继续 |
| 普通授权 checkout | 用户指令、repo-local contract、当前 Git/source facts | 合法；不伪造 Task/Run 或 managed-runtime 状态 |
| Managed production | runtime 注入的 Company snapshot、Task identity、授权 target 和 deployment lock | 按注入上下文执行；只在缺失、冲突或诊断时调用 status/doctor |

识别不到 managed Task identity 时，不得要求 task pointer 才能开始 construction 或普通授权工作。

## 路径与写入边界

- construction 的目标、source、repo、revision 和写入策略以外部 `BUILD-CONTEXT.md` 为准；
- managed production 只使用 runtime 注入的 company root、repo fleet 和授权 target；
- 普通 checkout 只在用户明确授权的工作树内写入；
- 不直接编辑 jarvis-box 管理的 state/env/cache 或任何凭据；
- provider-native session handle 属于 runtime 私有状态，不进入 Company Jarvis 或公开 handoff。

静态 Company Jarvis 不保存某台机器的绝对 runtime root、容器路径、凭据或可变 Task 状态。

## 何时检查 jarvis-box

只有处于 managed production 且发生以下情况时，才按当前产品 `--help` 使用对应
`jarvis-box status`、`agent current`、`doctor` 或 Task 观测命令：

- 注入的 Company context、Task identity 或授权 target 缺失；
- 注入上下文与当前 checkout/source 事实冲突；
- service、agent、connector 或 Task 明确需要诊断；
- operator 明确要求 runtime 运维检查。

正常业务会话不机械执行 `jarvis-box version/status/agent current`。运行时应在任务进入 Agent 前
完成上下文解析与注入，而不是把 discovery 成本推给每次会话。

## 升级到完整版

以下任一触发时，读取 [runtime-governance.md](runtime-governance.md) 对应章节：

- 路径、snapshot、identity 或 authority 冲突；
- Task 生命周期操作；
- service、agent、connector 或 deployment 配置变更；
- 凭据边界、Docker socket 或其他 host-root-equivalent 能力；
- 跨 target writeback 或 runtime 恢复。

service restart 只恢复服务能力，不等于继续旧 Task。只有 live 状态明确要求恢复时，才按证据
执行产品提供的恢复操作。
