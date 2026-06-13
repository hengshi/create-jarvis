# 试点 Workflow 方法论

选择并证明第一条 JARVIS 闭环时使用这份参考。

## 原则

从一条能产生证据的 workflow 开始，不要从“盘点全公司”开始。

好的第一条 workflow 应该有：
- 真实 owner / user；
- 公司中已经存在的真实 artifacts；
- 可观察 success signal；
- 有限 source/repo scope；
- 足够重复，值得沉淀 skill；
- 有人能判断结果是否有用。

## 推荐形态

1. 选择一条 workflow。
2. 命名 trigger 和 success signal。
3. 只 inventory 这条 workflow 需要的 sources 和 repos。
4. 搭建最小 entry skill、workflow skill、source skill、repo-local skill stubs。
5. 确认真值字段。
6. 用 3-5 个真实 artifacts 跑 shadow pilot。
7. 记录 failures 和 no-skill-gap decisions。
8. 只提升 durable learnings。

## 成熟阶段

- Installed：runtime 能 link instance，但 truth 未确认。
- First skill：entry skill 存在，可路由窄任务。
- Pilot-ready：first workflow、scope、owners、target paths 已确认。
- Pilot-proven：至少一条真实 START -> WORK -> END 有证据。
- Controlled ops：writeback 和 calibration 在 owner review 下运行。
- Enterprise runtime：多条 workflows 与 repo/source skills 由 owners 维护。
