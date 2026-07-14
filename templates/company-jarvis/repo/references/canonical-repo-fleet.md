# Canonical Repo Fleet

**状态**：强制 | **版本**：1.0

---

## 何时读取

在任何会话中首次进行 fleet 操作前读取；涉及多 repo 同步或缓存引用时读取。

## 核心规则

1. **已确认 source route 和对应 remote/VCS metadata 是仓库身份、访问入口和默认分支的权威来源。**
2. **工作修改只在授权 working tree 进行。**
3. **cache/workspace 路径、访问模式和同步 ownership** 仅从 `bootstrap-state.json`、`jarvis-box init`、`jarvis-box status` 及已安装产品证据获取；产品报告 cache 为只读时，agent 不把它当工作树。

## 仓库清单

### 已确认仓库范围

{{REPO_INDEX}}

### 仓库详情

| 仓库标识 | 身份/来源路由 | 角色 | 默认分支证据 | 访问状态 | repo-local 入口 | first-workflow 关联 |
|----------|--------------|------|-------------|---------|----------------|-------------------|
| BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED |

Phase 7 完成前必须用 pilot repos 和授权清单替换上表占位行。每行记录：

- **仓库标识**：canonical identity，来自实际 checkout 或 remote URL。
- **身份/来源路由**：该 repo 的来源路由，已确认的访问路径。
- **角色**：在 fleet 中的角色，来自 first workflow。
- **默认分支证据**：从当前 source route 对应的 live remote HEAD 或 VCS metadata 获取，不用当前 checkout branch，也不假定 remote 名称。
- **访问状态**：当前环境实际可访问性，不固定状态 taxonomy。
- **repo-local 入口**：该 repo 内的入口 skill 或指引文件。
- **first-workflow 关联**：该 repo 首次关联的工作流。

## 默认分支

- 默认分支从当前 source route 对应的 live remote HEAD 或 VCS metadata 获取。
- 不写死任何硬编码分支名。
- 每次 fleet 操作前从 remote truth 确认，不用缓存值。

## Fleet 操作

- Fleet 操作按已确认的 source route 进行。
- 任何 working change 只在授权 working tree 内。
- 路径、命令与同步策略只记录已安装产品或 source route 实际提供的合同。
- 已安装产品证据确认同步由 jarvis-box 管理时，company bootstrap 只检查和登记状态。

## 完成条件

- repo 的身份、角色、访问状态、默认分支、repo-local 入口和 workflow 关系均有实际 checkout、source route、remote/VCS metadata 或已安装产品 evidence。
- 所有路径和操作都能回指到当前客户环境的真实合同；未观察到的能力保持未登记，不用示例补全。
