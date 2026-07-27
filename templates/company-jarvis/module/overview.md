# {{MODULE_NAME}} 概览

## 模块身份

| 属性 | 值 |
|---|---|
| 模块名称 | {{MODULE_NAME}} |
| 所属公司 | {{COMPANY_NAME}}（slug: {{COMPANY_SLUG}}） |
| 产品身份 | {{PRODUCT_IDENTITY}} |
| Contract / decision authority | UNRESOLVED |
| Execution owner(s) | UNRESOLVED |
| 证据置信度 | UNRESOLVED |
| 确认状态 | UNRESOLVED |

## 业务定位

UNRESOLVED：以下内容必须根据已授权构件中的真实 evidence 填充。

- **业务目的**：UNRESOLVED — 用客户语言描述本模块做什么、谁依赖它、在 larger system 中的角色。
- **核心用户/角色**：UNRESOLVED
- **能力边界**：UNRESOLVED

## 首跳路由

UNRESOLVED — 从 company entry skill 进入本模块的第一跳路由规则：

| 触发信号 | 路由到 | 首个验证 |
|---------|--------|---------|
| UNRESOLVED | UNRESOLVED | UNRESOLVED |

## First Proof

UNRESOLVED — 代表性任务进入本模块后的第一个可验证证据点：
- **证据类型**：UNRESOLVED（issue / MR / commit / test / doc / alert）
- **预期行为**：UNRESOLVED
- **验证方式**：UNRESOLVED

## 常见 False Owner

UNRESOLVED — 哪些信号容易被误路由到本模块（以及实际应路由到哪里）：

| 误路由信号 | 实际归属 | 原因 |
|-----------|---------|------|
| UNRESOLVED | UNRESOLVED | UNRESOLVED |

## 证据与入口

每条证据使用可复查的 source pointer。代码实现使用 `<repo-name>:<repo-relative-path>`，路径必须在授权 checkout 中存在；产品证据使用对应 source route 能重新到达的文档、UI、API、issue 或测试 pointer。

| 证据类型 | 证据指针 | 观察到的事实 | 获取/检查方式 |
|---------|---------|------------|-------------|
| product | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| implementation | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| behavior / verification | UNRESOLVED | UNRESOLVED | UNRESOLVED |

included software module 至少要有一条 product anchor 和一条实际读取过的 implementation anchor。不得使用仅 repo 名、`service/` 这类泛化顶层目录、`model/ + service/`、construction 机器绝对路径，或“文件存在”替代具体证据与语义观察。

## 模块关系

UNRESOLVED — 在代表性任务、产品行为或已知产品拓扑中与其他模块的依赖关系：

| 方向 | 关联模块 | 耦合性质 | 接口 |
|------|---------|---------|------|
| UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |

## 搜索与验证

UNRESOLVED — agent 在本模块工作时应使用的搜索策略和验证入口：

- **代码搜索**：UNRESOLVED
- **Issue 追踪**：UNRESOLVED
- **变更历史**：UNRESOLVED
- **测试入口**：UNRESOLVED
- **CI/CD 入口**：UNRESOLVED

## 注意事项

- 本文件是路由导向的高信号文件，不复制源代码或原始 issue 内容。
- 接口、端点、路由、版本、数量等精确值来自 evidence inventory；无证据时写 `needs-verification`。
- 深层的 bug 模式属于 `known-issues.md`，持久设计选择属于 `decisions.md`。
- source 中检测到的产品/品牌名在 owner 确认前记为 `needs-owner-confirmation`。
- 不包含角度括号占位符、虚构的稳定端点、版本、日期、数量或技术栈选择。
