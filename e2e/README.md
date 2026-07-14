# Customer Bootstrap E2E

这份 runbook 用于验证从空 runtime 到 company Jarvis repo、再到 repo-local skills 的主链路。

它验证的是产品化契约，不验证某个真实 provider 的账号登录。空容器中 Codex / Claude / Copilot 通常会保持 `auth-pending`；真实客户现场需要 operator 在本机完成 selected bootstrap agent 的登录和命令行对话。

## 覆盖范围

- 在干净 Ubuntu systemd 容器中安装 jarvis-box。
- 使用本地 jarvis-box release artifact，避免依赖发布渠道。
- 挂载当前 `create-jarvis-skill` 工作树作为 method repo。
- 从调用方提供的 repo cache 或 Git URL 克隆客户 repo 测试副本。
- 删除测试副本中的 repo-local skill 目录。
- 通过真实 `jarvis-box bootstrap jarvis --non-interactive` 调起受控 bootstrap agent。
- 生成 company Jarvis repo。
- 为每个测试 repo 重新生成最小 `skills/` 目录包。
- 用 `scripts/verify_bootstrap_output.py` 校验 company Jarvis、repo-local skills、precheck、source dump 边界和 secret 边界。
- 校验 `jarvis-box doctor`。

## 不覆盖范围

- 不自动完成 Codex / Claude / Copilot provider 登录。
- 不读取真实 secret。
- 不把内部 repo 名写入通用方法仓库。
- 不把受控 bootstrap agent 当作真实 LLM 质量评估。
- 不安装 Phase 14 scheduled jobs。

## 输入

`scripts/run_customer_bootstrap_e2e.sh` 需要：

- `JARVIS_BOX_SRC_DIR`：jarvis-box 源码目录，必须包含 `install.sh`。
- `JARVIS_BOX_DIST_DIR`：jarvis-box release artifact 目录，必须包含 `SHA256SUMS` 和 linux tarball。
- `E2E_REPO_SPECS`：逗号分隔的 repo specs，格式为 `name=container-visible-git-source`。

如果使用本地 bare repo cache，把 host cache 目录挂载为 `/repo-cache`：

```bash
E2E_REPO_CACHE_DIR=/path/to/repo-cache \
E2E_REPO_SPECS="frontend=/repo-cache/frontend.git,backend=/repo-cache/backend.git" \
JARVIS_BOX_SRC_DIR=/path/to/jarvis-box \
JARVIS_BOX_DIST_DIR=/path/to/dist \
scripts/run_customer_bootstrap_e2e.sh
```

## 输出

默认输出在：

```text
.eval-runs/customer-bootstrap-e2e/<timestamp>/
├── customer-repos/
├── output/company-jarvis/
├── bootstrap-verify-report.json
├── bootstrap-verify-findings.md
├── bootstrap-verify-stdout.json
└── jarvis-box-doctor.txt
```

关键验收点：

- `bootstrap-verify-report.json` 的 `status` 是 `pass`；
- `output/company-jarvis/README.md`、`MAINTENANCE.md`、`jarvis.toml`、`bootstrap-state.json`、`bootstrap-result.json` 存在；
- company entry skill 位于 `output/company-jarvis/skills/<company>-jarvis/SKILL.md`；
- company Jarvis 具有 `modules/`、`sources/`、`cross-cutting/`、`references/`、`skills/`、`tools/`、`evals/` 这些 `hengshi-jarvis` 风格核心目录；
- company Jarvis 不包含顶层 `repos/`、`workflows/`、`pilot/`、`writeback/`、`rollout/`、`scheduled-jobs/`；
- `output/company-jarvis/bootstrap-result.json` 的 status 是 `completed`、`needs-input`、`blocked` 或 `failed` 中的合法值；受控 e2e 通常是 `needs-input`，因为它不做 owner 确认和影子试跑；
- 当 `jarvis-box bootstrap jarvis --non-interactive` 因 `needs-input` 或 `blocked` 返回非零时，e2e 继续运行 verifier；只有 result contract 不可解析、verifier fail 或状态非法时才算 e2e 失败；
- 每个 `customer-repos/<repo>/skills/` 包含 10 个核心文件；
- 每个 `customer-repos/<repo>/skills/code-review/scripts/precheck.sh` 可执行，并能定位到 repo root；
- company Jarvis repo 不包含客户源码目录、源码文件精确副本、明显 secret 或 bearer token；
- `jarvis-box-doctor.txt` 包含 `summary=ok`。

## 结果解释

该 e2e 通过时，说明：

- 大步骤一的安装主链路可运行；
- jarvis-box 能把 bootstrap 调用交给 runtime agent；
- create-jarvis-skill 的机器输出契约可以被 jarvis-box 接受；
- company Jarvis repo 与 repo-local skill bootstrap 可以串起来。
- 缺 owner 确认、identity reconciliation、shadow pilot 时，bootstrap 结果会诚实停在 `needs-input`。

该 e2e 不能证明：

- selected bootstrap agent 已在客户现场完成真实登录；
- 生成物已经达到 `acceptance.md`；
- modules 已经从客户产品/业务证据中正确提炼；
- first workflow 已经完成 START -> WORK -> VERIFY -> END 语义闭环；
- repo-local skills 已成熟；
- 生成的 repo 命令已被 repo owner 确认；
- 第二天运营所需 runtime tools 和 scheduled jobs 已安装。

## 真实 Claude e2e

`scripts/run_apple_container_claude_e2e.sh` 使用 Apple `container` CLI 跑真实 Claude Code：

- 用 `Dockerfile` / `Containerfile` 构建轻量 Ubuntu image；
- 安装 Node.js 22 和 `@anthropic-ai/claude-code`；
- 从本机 `~/.zshrc` 读取 `ANTHROPIC_*` 到临时 env-file；
- env-file 只在本次运行期间存在，脚本退出时删除；
- 不复制 Claude home / local auth state 到 e2e 产物；
- 挂载当前 `create-jarvis-skill` 工作树为只读 method repo；
- 使用本地 jarvis-box Linux artifact；
- 调用真实 `jarvis-box bootstrap jarvis --non-interactive`；
- `JARVIS_BOOTSTRAP_AGENT_CMD` 指向 Claude wrapper；
- 复用 `scripts/verify_bootstrap_output.py` 验收 company Jarvis repo 和 repo-local skills。

示例：

```bash
E2E_REPO_SPECS="lhotse=/repo-cache/lhotse.git,everest=/repo-cache/everest.git" \
E2E_REPO_CACHE_DIR=/Users/thomaschan/.hengshi/repo-cache \
JARVIS_BOX_DIST_DIR=/tmp/jarvis-box-install-e2e/dist \
scripts/run_apple_container_claude_e2e.sh
```

这条 e2e 不验证 jarvis-box systemd service install；systemd install 仍由 Docker e2e 覆盖。它验证真实 runtime agent 能否按方法论生成 `hengshi-jarvis` 风格的 company Jarvis repo、repo-local skill package、first routing references，并通过统一机器防呆检查。

真实 Claude e2e 的 verifier 通过后，还必须按 `acceptance.md` 审查结果。若生成物只有通用 scaffold、通用工程层 modules 或缺少 evidence-backed first workflow，不得称为 bootstrap 完成。
