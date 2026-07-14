# {{MODULE_NAME}} 概览

## 模块身份

| 属性 | 值 |
|---|---|
| 模块名称 | {{MODULE_NAME}} |
| 所属公司 | {{COMPANY_NAME}}（slug: {{COMPANY_SLUG}}） |
| 产品身份 | {{PRODUCT_IDENTITY}} |
| 能力负责人 | {{COMPANY_OWNER}} |
| 证据置信度 | BOOTSTRAP_REQUIRED |
| 确认状态 | BOOTSTRAP_REQUIRED |

## 业务定位

BOOTSTRAP_REQUIRED：以下内容由 Phase 7 根据 _bootstrap/discovery/module-coverage-matrix.md 和 evidence-inventory.md 填充。

- **业务目的**：BOOTSTRAP_REQUIRED — 用客户语言描述本模块做什么、谁依赖它、在 larger system 中的角色。
- **核心用户/角色**：BOOTSTRAP_REQUIRED
- **能力边界**：BOOTSTRAP_REQUIRED

## 首跳路由

BOOTSTRAP_REQUIRED — 从 company entry skill 进入本模块的第一跳路由规则：

| 触发信号 | 路由到 | 首个验证 |
|---------|--------|---------|
| BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED |

## First Proof

BOOTSTRAP_REQUIRED — 本模块在 first workflow 中的第一个可验证证据点：
- **证据类型**：BOOTSTRAP_REQUIRED（issue / MR / commit / test / doc / alert）
- **预期行为**：BOOTSTRAP_REQUIRED
- **验证方式**：BOOTSTRAP_REQUIRED

## 常见 False Owner

BOOTSTRAP_REQUIRED — 哪些信号容易被误路由到本模块（以及实际应路由到哪里）：

| 误路由信号 | 实际归属 | 原因 |
|-----------|---------|------|
| BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED |

## 证据与入口

每条证据行使用可解析格式 `<repo-name>:<repo-relative-path>`，路径必须在授权 checkout 中存在。

| 证据指针 | 观察到的事实 | 获取/检查方式 |
|---------|------------|-------------|
| BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED |

至少一条证据必须来自 _bootstrap/discovery/evidence-inventory.md 中实际执行过检索的 repo/source。不得使用仅 repo 名、`service/` 这类泛化顶层目录、`model/ + service/` 或 bootstrap 机器绝对路径替代具体证据指针。

## 模块关系

BOOTSTRAP_REQUIRED — 在 first workflow 或已知产品拓扑中与其他模块的依赖关系：

| 方向 | 关联模块 | 耦合性质 | 接口 |
|------|---------|---------|------|
| BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED |

## 搜索与验证

BOOTSTRAP_REQUIRED — agent 在本模块工作时应使用的搜索策略和验证入口：

- **代码搜索**：BOOTSTRAP_REQUIRED
- **Issue 追踪**：BOOTSTRAP_REQUIRED
- **变更历史**：BOOTSTRAP_REQUIRED
- **测试入口**：BOOTSTRAP_REQUIRED
- **CI/CD 入口**：BOOTSTRAP_REQUIRED

## 注意事项

- 本文件是路由导向的高信号文件，不复制源代码或原始 issue 内容。
- 接口、端点、路由、版本、数量等精确值来自 evidence inventory；无证据时写 `needs-verification`。
- 深层的 bug 模式属于 `known-issues.md`，持久设计选择属于 `decisions.md`。
- source 中检测到的产品/品牌名在 owner 确认前记为 `needs-owner-confirmation`。
- 不包含角度括号占位符、虚构的稳定端点、版本、日期、数量或技术栈选择。
