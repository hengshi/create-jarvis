# 版本变更索引

> 客户版本/发布事实的索引和路由，不复制 release 内容。
> 当客户有版本管理实践时记录 source-of-truth 和访问方式；当客户没有版本概念时允许 evidence-backed not-applicable。

---

## 版本源配置

| 字段 | 值 |
|------|-----|
| Source of truth | BOOTSTRAP_REQUIRED — Phase 7 根据客户实际版本管理方式配置 |
| 访问/检索方式 | BOOTSTRAP_REQUIRED |
| 产品/范围 | BOOTSTRAP_REQUIRED |
| 状态 | BOOTSTRAP_REQUIRED |

若客户经 evidence 确认无版本管理实践，在此记录 `not-applicable` 及证据来源，不虚构版本基础设施。

---

## 版本线索引

### 当前活跃版本

| 版本 identity | Source pointer | 受影响 modules / delivery surfaces | 状态 |
|-------------|---------------|---------------------------|----|
| （bootstrap 尚未登记任何版本线） | — | — | — |

### 历史版本

| 版本 identity | Source pointer | 受影响 modules / delivery surfaces | 状态 |
|-------------|---------------|---------------------------|----|
| （bootstrap 尚未登记任何历史版本） | — | — | — |

**字段说明**：

- **版本 identity**：客户使用的版本标识（由客户版本源决定，不预设 semver、日期版、代号等格式）。
- **Source pointer**：版本信息的权威来源位置（不复制内容，只记录到达路径）。
- **受影响 modules / delivery surfaces**：该版本变更涉及的模块或交付面。
- **状态**：使用版本权威来源中的实际状态；客户没有版本概念时记录 `not-applicable` 及证据。

---

## 配合使用

- `cross-cutting/module-interactions.md` — 跨模块影响
- `modules/*/known-issues.md` — 模块级问题模式
- `modules/*/rejected-features.md` — 被否决的需求

---

## 使用说明

- 本文件是版本变更的索引与路由辅助，不复制 changelog 或 release note 正文。
- 版本 identity、来源和检索方式全部来自客户证据。
- 如果已有更好的 release-note source，链接过去，不复制内容。
