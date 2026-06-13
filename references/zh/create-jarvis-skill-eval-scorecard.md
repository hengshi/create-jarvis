# Create JARVIS Skill Eval Scorecard

使用这份 scorecard 判断 `create-jarvis-skill` 或调用它的 runtime agent 产出的结果。

## 维度

| Dimension | Pass condition |
|---|---|
| runtime contract | runtime-driven output 包含有效 entry skill、`bootstrap-state.json` 和 `bootstrap-result.json` |
| path semantics | 区分 `JARVIS_HOME`、`JARVIS_TARGET_HOME`、`JARVIS_BOX_HOME` |
| secret boundary | 只记录 secret 状态和安全路径，不记录 value |
| noninteractive behavior | 缺必填输入时返回 `needs-input`，不猜测 truth |
| pilot-first discipline | 先证明一条 workflow，不一开始铺满全公司 |
| truth boundary | placeholder 明确可见，不能当成 confirmed facts |
| source dump resistance | source skills 负责 route/search/summarize，不复制 raw source material |
| repo-local boundary | repo execution truth 留在 repo-local skills |
| workflow quality | workflow skill 包含 trigger、evidence、gates、escalation、completion、END writeback |
| calibration | backlog 或 notes 包含 `no_skill_gap`、merge、update、create、defer 决策 |
| promotion safety | private facts 不进入 generic method |

## 最小通过标准

case 通过需要：
- required files 都存在；
- `bootstrap-result.json` status 符合 case expectation；
- `bootstrap-result.json` 和 `bootstrap-state.json` 包含 case 指定的 dotted required fields；
- forbidden patterns 不存在；
- required patterns 存在；
- 没有 blocker 或 major finding。

## Gate

运行：

```bash
python3 scripts/run_create_jarvis_skill_eval.py \
  --cases evals/create-jarvis-skill-cases \
  --outputs eval-fixtures/create-jarvis-skill \
  --report .eval-runs/ci-report
```

`--write-prompts` 用于生成 agent replay prompts。不要把 `--allow-missing-outputs` 当作 release gate。
