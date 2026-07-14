# Intake Disposition 矩阵

先做 claim 归一化，再用此矩阵定 disposition。细粒度判断见 `pre-filing-judgment-card.md`。

| Outcome | 何时使用 | 建新 issue？ | 关键输出 |
| --- | --- | --- | --- |
| `ready-to-file-bug` | Supported 能力出现真实行为差异，非 duplicate/by-design | 是 | Bug/regression markdown |
| `ready-to-file-feature` | 真实新需求或增强，非历史被拒绝方向 | 是 | Feature/enhancement markdown |
| `duplicate` | 已知问题模式/已有 issue/历史记录覆盖当前主要问题 | 否 | 指向已有线索，说明为何不重复建 |
| `by-design` | 当前行为被产品边界或设计决策解释 | 否 | 设计边界、已知限制、可用 workaround |
| `rejected-request / wontfix-history` | 需求方向已被明确拒绝或有 wontfix 历史 | 否 | 历史结论，不换标题重提 |
| `blocked-needs-evidence` | 尚不能判定真 bug/真需求，也不能排除其他结论 | 否 | 缺口清单 + 下一轮补什么 |

## 使用原则

- Reporter 标的 bug/feature/enhancement/question 只是假设，不是最终结果。
- `question / usage clarification` 不是最终结果；必须解析为 by-design/blocked/feature filing。
- 下 duplicate/by-design/rejected 结论前，先执行 `disposition-command-checklist.md` 证据动作，再按 `disposition-proof-sop.md` 做实查。
- 结论默认包含 overlap/delta。
- 非 filing 结果也必须携带可直接沟通的转发话术。

## 各 Outcome 要点

### ready-to-file-bug
受影响 surface/工作流、复现步骤或观察路径、期望 vs 实际、环境身份、是否有 workaround 均需明确。如之前能用现在坏了标注回归信号。如看起来更像数据/配置/权限问题先确认 supported flow 是否真的坏了。

### ready-to-file-feature
目标用户、场景、当前方式、缺口、期望结果和基本验收标准均需明确，并说明该请求与 {{PRODUCT_IDENTITY}} 已确认 scope 的关系。增强请求也归此结果，在正文中区分 feature 与 enhancement。

### duplicate
不建新 issue。说明命中了哪个已知问题/已有 issue。说明此输入增加了什么新证据。如有 workaround 告知 reporter。如候选 issue 声称已修复，增加 fix scope 是否覆盖当前症状的验证。不应误判：表面相似但触发条件/根本行为差异不同。

### by-design
不建新 issue。明确说明哪个设计/产品边界在起作用、为什么适用于当前场景、为什么解释实际结果。如有 workaround 或替代路径记录。如 reporter 实际在提需求判断是否进入 ready-to-file-feature。

### rejected-request / wontfix-history
不建新 issue。说明命中哪个历史拒绝结论、当时的拒绝核心原因。如环境已实质性改变重新评估。引用真实来源而非二手摘要。

### blocked-needs-evidence
不建新 issue。不猜测填补空白。给出 blocker 清单说明已查什么还缺什么。只有适用于当前 claim、且 agent 能从授权 source 执行的证据动作已经穷尽后才进入此类。
