# Create Jarvis

`create-jarvis` 是客户从零建设、安装并启用一套 Jarvis 的 Agent 方法仓库。完整逻辑模型以 [GOAL.md](GOAL.md) 为准；本仓库不是安装器、construction daemon 或 jarvis-box 内部模板集合。

## 客户入口

客户在已经登录并授权的 Host Runtime Agent 中只需说：

> 请运行 `git clone https://github.com/hengshi/create-jarvis create-jarvis`，读取本地 `create-jarvis/SKILL.md`，然后帮我构建一套 Jarvis。

收到请求的 Agent 是 Construction Coordinator。它主持资料说明与 intake、创建可恢复 Construction Workspace、协调长任务、发布客户资产、安装 jarvis-box 并引导 onboarding。初始请求只授权克隆公共方法仓库；扫描 home、Agent 配置、历史记录或其他仓库都需要明确授权。

## 四部分旅程

```text
Part 1  Jarvis repo initialization
Part 2  Jarvis knowledge + Runtime Foundation construction
Part 3  independent repo-local learning for each code repository
Part 4  jarvis-box Docker runtime + Runtime Foundation bootstrap + onboarding
```

Part 2 与 Part 3 可并行。所有部分都通过 `jarvis-build/` 中的普通 Markdown work card、journal 和 evidence 恢复，不依赖原对话或某个 Agent 进程仍然存活。

```text
jarvis-build/
├── CONTINUE-JARVIS.md
├── CONSTRUCTION-JOURNAL.md
├── BUILD-CONTEXT.md
├── work/
│   ├── jarvis-repo-initialization.md
│   ├── jarvis-construction.md
│   ├── repositories/<repo>.md
│   ├── reconciliation.md
│   └── jarvis-box-onboarding.md
└── evidence/
```

## Runtime 边界

Jarvis repo 拥有 `runtime-governance.md` 和客户特有 Runtime Foundation。Runtime Foundation 在目标 Runtime Environment 的持久 Agent HOME 中维护 cache、stable jobs、state/log，并把 Jarvis skills/references 同步到 Agent 原生 discovery roots。

jarvis-box 只拥有 Task/Run、Agent 执行、control plane、runtime state/workspaces/logs 和 operator surface。它不 clone、pull、mount、校验或注入 Jarvis repo，也不读取 `runtime-governance.md`。

Docker 调度只改变外层调用：

```text
native scheduler ───────────────→ inner Runtime Job
host scheduler → release helper → same inner Runtime Job in Docker
```

内部的 sync、maintenance、self-improve 等任务不包含 `docker compose exec/run`。Docker image 也不包含 create-jarvis、客户 Jarvis 或客户 Runtime Foundation；这些通过 Part 4 bootstrap 进入持久 Agent HOME。

## Repository learning

学习单位是完整 episode，而不是 commit message 分类。真实问题缺失时，由上下文隔离的 reconstruction Agent 根据 pre-change state、diff、tests 与历史证据重建最小 visible START；Replay Agent 看不到真实结果。

```text
visible START → baseline replay → hidden outcome comparison
              → minimal skill delta → same-case rerun → adjacent regression
```

## 恢复话术

> 继续构建我们的 Jarvis。建设工作区是 `<path>/jarvis-build`。请读取 `CONTINUE-JARVIS.md` 和 `CONSTRUCTION-JOURNAL.md`，核验现有交付事实后从记录的 Next 继续，不要重新初始化已存在的工作。

执行入口见 [SKILL.md](SKILL.md)，跨产品总纲见 [GOAL.md](GOAL.md)，术语见 [CONTEXT.md](CONTEXT.md)。
