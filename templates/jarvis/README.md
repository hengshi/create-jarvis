# Jarvis templates

本目录保存 Jarvis construction agent 可选择使用的母版。母版只提供结构与稳定方法语义，不能代替客户事实。

```text
templates/jarvis/
├── repo/       # Jarvis repo 基础结构
├── module/     # 单个Jarvis/产品 module 的持久知识结构
└── source/     # source route contract
```

## 所有权边界

- Jarvis 保存Jarvis 级入口、语义、module/source/repo 路由与跨 repo workflow。
- repo 内工程执行真相留在对应代码仓库的 repo-local skills。
- runtime-owned skills 和 jarvis-box 能力不复制进 Jarvis repo。
- 不生成 `jarvis.toml` 或 construction state files。

## 渲染事实

construction agent 从 `BUILD-CONTEXT.md` 指向的真实证据确认渲染值。缺失或冲突的客户事实必须保持 unresolved，不能用模板默认值冒充。

构建按 `playbooks/prompts/jarvis-construction.md` 对声明授权范围持续做 capability/source/repo coverage；模板只创建安全容器，不能作为“构建完成”的证据。

当前母版使用的主要 token：

| Token | 含义 |
|---|---|
| `{{JARVIS_NAME}}` | 已确认Jarvis名称 |
| `{{JARVIS_SLUG}}` | 已确认 slot/slug |
| `{{JARVIS_PURPOSE}}` | 已确认产品/业务身份；未确认时明确 unresolved |
| `{{JARVIS_OWNER}}` | 当前 owner；未知时明确 unresolved |
| `{{MODULE_NAME}}` | 从客户证据得到的 module 名称 |
| `{{SOURCE_NAME}}` | 已授权 source 名称 |
| `{{SKILL_NAME}}` | Jarvis-owned skill 名称 |

母版不能包含客户专有 host、repo、issue、owner、源码、文档正文、凭据或私有路径。
