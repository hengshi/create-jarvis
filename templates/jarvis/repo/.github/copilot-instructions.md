<!-- {{JARVIS_SLUG}}-jarvis:begin -->
{{JARVIS_NAME}} JARVIS POINTER

- {{JARVIS_SLUG}}-jarvis 是 {{JARVIS_NAME}} 企业闭环统一入口，非单纯 repo router。
- 每次任务先读 `references/runtime-governance-quick.md`，再判断是 construction、普通授权 checkout 还是 managed production；construction 不依赖 jarvis-box。
- Canonical entry skill: `skills/{{JARVIS_SLUG}}-jarvis/SKILL.md`
- Workflow-first when active：有已验证 workflow 时按闭环选择；尚无 active workflow 时只做 module/source/first-proof routing，不冒充生产闭环。
- Artifact-first：有 issue / MR / error / screenshot / URL / failing test 时，从 artifact 路由。
- Repo-local truth：repo 内工程执行方法留在 repo-local skills。
- Redaction：不把源代码、密钥、私密信息复制进此 repo。
- 修改 {{JARVIS_SLUG}}-jarvis 本身时遵循 `MAINTENANCE.md`。
<!-- {{JARVIS_SLUG}}-jarvis:end -->
