# Workflow Runtime Contract v1

本文件约束 Customer Workflow 如何与 `jarvis-box` 交换当前 Run 的输入、结果和受控 actions。它是运行协议，不定义本客户的 outcome、标签、状态、审批或路由语义；这些语义必须在客户 workflow 中由真实证据确定。

## 输入

当 run 目录存在 `workflow-input.json` 时，先读取并保留以下边界：

- `schema_version`、`workflow_type`；
- `inputs`：上一个 Customer Workflow 交付的不透明 JSON object；
- `provider_event` 与唯一 `subject` identity；
- Task、Run、Run Dir 与已登记 Workspace IDs；
- `allowed_actions`：本 Run 唯一可请求的副作用集合。

不得把候选实现仓库、客户知识 repo 或当前工作目录替换成 input subject；不得假设未列入 grant 的 provider、project、workflow 或操作也可用。

## 结果

退出前原子写出 `workflow-result.json`：

```json
{
  "schema_version": 1,
  "status": "completed",
  "summary": "给人的简短结论",
  "outcome": {"customer_defined": "opaque-to-jarvis-box"},
  "actions": []
}
```

- `status` 只能是 `completed`、`blocked`、`needs-input`；
- `summary` 必须能让 operator 明白当前结果；
- `outcome` 完全属于 Customer Workflow，`jarvis-box` 不解释；
- 所有外部副作用必须逐条成为显式 action。没有 action 就没有副作用；
- action `id` 在结果内唯一，供重试去重和审计使用。

v1 支持的 action：

- `provider.comment.create`：精确复制 input subject 的 `provider`、`project`、`subject_id`，正文来自安全的 run-relative `body_artifact`；
- `provider.issue.labels.add`：只请求已确认存在的精确 labels，不提交候选值；
- `provider.issue.status.set`：只请求客户 policy 已授权的精确 status；
- `workflow.start`：只请求 grant 中列出的 `workflow_type`，`inputs` 必须是 JSON object，承载下一个 workflow 需要的客户数据。

禁止 shell action、绝对 artifact path、路径逃逸、任意 provider/project target，或让 `jarvis-box` 根据 outcome 猜 mutation / next workflow。写完后重新读取 input/result，核对 schema、subject identity、grant 和 artifact。

## Customer Workflow 客户化门槛

Standard Workflow Pack 里的 action 示例不是客户 policy。Construction 时必须用客户真实事实回答：

- 哪些结果应该公开 comment；
- 哪些 labels/status 真实存在、谁有权修改、在哪一步修改；
- 哪些 outcome 请求哪个下一 workflow；
- 下一 workflow 需要哪些 inputs 和 Workspace/resource 前提；
- blocked / needs-input 时允许做哪些最小动作。

至少用一个真实或等价 case 验证 result 校验、provider 写回、next workflow 与重试审计后，才能把 workflow 标为 verified。
