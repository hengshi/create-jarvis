# Agent-native company Jarvis bootstrap

把下面这段话交给已经登录并可访问客户授权材料的 Codex、Claude 或其他 runtime agent。不要先运行一份 bootstrap 表单，也不要要求客户替 agent 在多个 session 之间转发 handoff。

```text
请使用 create-jarvis-skill，在当前已授权环境中为这家公司构建或继续构建 company Jarvis。

先读取 create-jarvis-skill 的 GOAL.md、SKILL.md、acceptance.md 和 phase checklist。然后自行探测当前身份、`JARVIS_WORKSPACE_ROOT` 或其他可写 workspace、已有 bootstrap-state.json、Git/VCS 能力，以及我已经授权的 repos、docs、issues/MRs、tests 和 CI。不要把 service-private `JARVIS_RUNTIME_ROOT` 当作 agent workspace。优先从这些证据中发现公司/产品身份候选、业务模块、repo 角色、source routes、first workflow 和验证入口；不要先向我发一份长表单。

只有以下信息无法从当前环境安全得到时才问我：授权范围或身份冲突的确认、必要凭据/访问、对外写入或建仓审批，以及多个真实 workflow 候选之间的业务选择。对可逆的本地路径、slug、扫描顺序和 local-only 草稿采用安全默认值，并把推导依据写入 bootstrap state。

你是本次 bootstrap 的协调者。可并发时自行派发扫描或 replay lane；不可并发时在当前任务内顺序执行并从持久 state 继续。不要让我新开 session、复制 prompt 或搬运 agent 结果。

按 Phase 3-14 推进。任何阶段不满足门禁时，诚实记录 needs-input / blocked / failed 和精确下一步；不要把模板生成或 verifier 通过当成 company Jarvis 完成。
```

可选地在这段话后补充公司名和一组 repo/docs URL。其余内容应先由 agent 发现，再只确认不可推导的决策。
