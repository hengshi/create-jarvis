# Create JARVIS Skill（中文）

> 英文版：`README.md`

这个仓库用于**指导 agent 为某家公司搭建公司专属 JARVIS**：
- 先把“第一条可验证的业务闭环”选对
- 再盘点这条闭环所涉及的 sources / repos / workflows
- 生成最小可用的骨架与技能骨架
- 强制人工确认承载事实的字段
- 通过 shadow pilot、START → WORK → END、failure calibration 和 controlled writeback，让 JARVIS 逐步变成熟

## 你应该从哪里开始

- **唯一 golden path：`SKILL.md`**（主干流程、默认顺序、停点、交付物）

> 当前版本里：
> - `references/en/` 与 `references/zh/` 采用**同名镜像文档**结构
> - `templates/en/` 与 `templates/zh/` 采用**同名镜像模板**结构
> - `SKILL.md` 仍然是唯一权威执行路径；中英文辅助文档只是在不同语言下表达同一结构语义

## 这项目是什么 / 不是什么

### 是什么
它是一个“元 skill”：帮助 agent 把一家公司的数字资产、代码仓库、跨团队流程，逐步变成可执行、可维护、可持续迭代的组织能力（而不只是知识库）。

### 不是什么
- 不是“一次性生成一个漂亮的知识仓库”
- 不是把原始材料整段复制进文档
- 不是承诺一个 agent 一次会话就能完成企业级 rollout
- 不是替代 repo 内的权威来源
- 不是替代 jarvis-box 的 runtime install/setup/service/task 逻辑

## 四层生态 + runtime 层

JARVIS rollout 至少要分清：

1. **中心 JARVIS entry skill**：负责闭环识别、routing、索引、next-hop selection、END writeback 判断。
2. **Source skills**：负责访问和理解 docs、issues、BI、support、会议记录等 source，不复制 source 内容。
3. **Repo-local skills**：负责 repo 内部执行真相，例如 build/test/run、验证、安全修改、repo-local writeback。
4. **Workflow skills**：负责跨 source / repo / team 的闭环、gate、artifact、handoff、完成证据。

runtime 层由 jarvis-box 或其他 runtime 负责：install、setup、credentials、webhooks、task execution、state、logs、service lifecycle。本仓库负责 methodology、scaffold、pilot、writeback 和 calibration contracts。

## 推荐用法（最小可用）

1. 让 agent 阅读 `SKILL.md`
2. 先把“第一条闭环”与“成功信号”说清楚
3. 用模板盘点试点范围内的 sources / repos / workflows
4. 生成最小骨架 + 必要的 skill 骨架
5. 做一次人工确认（不要把占位符当真相）
6. 进入 shadow pilot，用真实 artifacts 跑至少一条 START → WORK → END
7. 通过 `no_skill_gap` / merge / update / create 决策校准 skill
8. 只把 durable learning 回写到正确层级

## jarvis-box 等 runtime 调用方

jarvis-box 应该通过配置好的 runtime agent 调用这个仓库，而不是把本仓库 templates 复制进 jarvis-box。runtime 负责提供 `JARVIS_TARGET_HOME`、`JARVIS_COMPANY_NAME`、`JARVIS_FIRST_LOOP`、GitLab 范围、owners 和回写策略；本仓库负责方法论和输出契约。

在 runtime 模式下，agent 必须在目标 home 中创建有效的 `$JARVIS_HOME/SKILL.md`、bootstrap 产物、`bootstrap-state.json` 和尽可能机器可读的 `bootstrap-result.json`。使用 `JARVIS_HOME`、`JARVIS_TARGET_HOME`、`JARVIS_BOX_HOME` 这类中性 runtime 变量，不要假设客户 runtime root 使用 Hengshi 命名。默认 method repo URL 是 `https://github.com/hengshi/create-jarvis-skill.git`。

如果 `JARVIS_NONINTERACTIVE=1` 且缺少必填输入，agent 不应猜测 owner、source-of-truth 或 workflow，而应返回 `needs-input` / blockers。

## 双语结构

```text
create-jarvis-skill/
├── README.md
├── README.zh.md
├── SKILL.md
├── references/
│   ├── en/
│   │   ├── positioning.md
│   │   ├── company-adaptation.md
│   │   ├── instance-generation-contract.md
│   │   └── ...
│   └── zh/
│       ├── positioning.md
│       ├── company-adaptation.md
│       ├── instance-generation-contract.md
│       └── ...
└── templates/
    ├── en/
    │   ├── jarvis-build-brief.md
    │   ├── source-inventory.md
    │   ├── repo-inventory.md
    │   └── ...
    └── zh/
        ├── jarvis-build-brief.md
        ├── source-inventory.md
        ├── repo-inventory.md
        └── ...
```

## 使用原则

- `SKILL.md` 负责主干方法与执行顺序。
- `references/en/*.md` 与 `references/zh/*.md` 是**一一对应的镜像参考文档**。
- `templates/en/*.md` 与 `templates/zh/*.md` 是**一一对应的镜像模板**。
- 修改结构语义时，应优先更新英文与中文镜像，使同名文件保持契约一致。
- 不要新增 `SKILL.zh.md`；避免出现双份主流程导致漂移。
- 内部公司经验要先经过 repo-local → central JARVIS → generic create-jarvis-skill 的 promotion ladder，脱敏并证明可复用后才能上升到本仓库方法论。

## 许可说明

© 2026 [Hengshi](https://github.com/hengshi)。保留所有权利。

JARVIS 是付费咨询产品。这个 skill 提供给已获许可的用户，用于启动他们的 JARVIS 知识库建设。

如需咨询许可或合作：
- 🌐 [hengshi.com](https://hengshi.com)
- 📧 hi@hengshi.com
- 📞 15810120570
