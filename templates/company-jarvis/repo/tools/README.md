# 工具索引

公司 Jarvis 自己拥有的高信号可复用辅助工具索引，也登记 Company runtime governance 要求的客户级 Host 工具。不复制 repo-local 或 jarvis-box/install-owned capability。

稳定的 maintenance/self-improve 实现位于 `../runtime-foundation/`。本目录只放 Company Jarvis 的其他工具，不要在这里再生成一套 scheduler 或复制 Runtime Foundation job。

---

## 什么适合放在这里

- 能节省 agents 重复劳动的客户特有辅助脚本
- 稳定的查询或检查辅助工具
- 与重复 workflow 绑定的操作手册
- 客户 runtime governance 要求、由客户维护的 sync/workspace/handoff 辅助工具

## 什么不适合放在这里

- 随机的一次性实验
- 没有 Jarvis-specific 价值的通用工具
- 更适合保留在 source repos 中的大型操作手册
- 由当前安装的 jarvis-box 或其他 runtime 已经拥有的 capability
- 没有来源和验证证据的候选工具

---

## 公司特有工具清单

工具存在时记录以下字段；不存在时保持空表。

| identity | owner | source | 用途 | 调用入口 | 前提/权限 | secret boundary | 验证方式 | 状态 |
|---------|-------|--------|------|---------|----------|---------------|--------|----|
| （初次构建尚未登记任何公司特有工具） | — | — | — | — | — | — | — | — |

**字段说明**：

- **identity**：工具的唯一标识名。
- **owner**：维护该工具的负责人或团队。
- **source**：工具的来源位置（不复制工具本身，只记录到达路径）。
- **用途**：一句话描述工具解决什么问题。
- **调用入口**：agent 或人如何调用该工具。
- **前提/权限**：调用前需满足的条件（认证、环境、依赖等）。
- **secret boundary**：工具涉及哪些密钥或敏感信息，以及它们的隔离边界。
- **验证方式**：如何确认工具仍然可用且行为正确。
- **状态**：记录当前实际可用性及其验证证据。

状态使用 `unresolved`、`documented`、`implemented`、`verified` 或 `pending-runtime-foundation`。需要安装机制的工具只有在稳定入口实际安装并运行验证后才能写 `verified`。

---

## 调度任务

若存在 scheduled job，只记录其真实 owner 和 source route，不在本文件规定固定目录或调度基础设施。

（初次构建尚未登记任何调度任务）

---

## 工具创建原则

- 优先使用 stdlib 和已安装依赖，不为简单辅助逻辑引入新依赖
- 脚本应有明确的单点用途
- 每个工具在本文件登记一条记录
- 工具在被 agents 调用前应经过验证
- 临时 construction checkout 不能冒充长期稳定调用入口
- install、sync、upgrade 与 rollback owner 必须明确

---

## 使用说明

- 添加新工具时按上述字段在本文件登记。
- runtime 已拥有的 capability 只记录其权威入口，不复制实现到 company Jarvis。
