# Part 4: Jarvis Box installation and onboarding

Use this card only after reconciliation and at least one customer workflow are verifiably `construction-ready`. Construction does not depend on Jarvis Box.

Read `work/jarvis-box-onboarding.md`. After every material checkpoint, record the observed fact, evidence and `Next`. Do not copy Jarvis Box implementation details into the card.

## 1. Freeze the handoff

Resolve from delivered evidence:

- approved Company Jarvis remote and commit;
- required repository remotes, commits and repo-local entry skills;
- selected workflow and its source revision;
- customer Jarvis Runtime Foundation bootstrap, sync and doctor entries;
- selected Jarvis Box release version;
- customer-approved provider, source, Agent and optional connector authority.

Do not deploy dirty checkouts, unresolved refs, floating images or unpublished local skills. If reconciliation cannot be reproduced, return to reconciliation instead of starting a partial runtime.

## 2. Ask one deployment question

Ask the customer: **Native or Docker?**

| Mode | Runtime owner | Authentication |
| --- | --- | --- |
| Native | the existing OS user that starts installation | reuse that user's authorized `gh`, `glab`, Codex, Claude and source identities |
| Docker | a persistent runtime inside the container boundary | import only approved portable identities from the current Host user |

A dedicated machine account is an optional customer policy, not an installation prerequisite. Never copy Host HOME, SSH agent, Keychain, complete credential stores or raw tokens into Company Jarvis, the Construction Workspace or evidence.

Record the selected mode before continuing. Do not ask the customer to understand Compose, env-file ownership or container paths unless a concrete Docker configuration decision requires it.

## 3. Use the Jarvis Box public contract

Download and verify the public release bundle. Treat its customer operations manual and public installer/helper as the only deployment procedure.

`create-jarvis` depends only on these public facts:

- installation or upgrade entry;
- Native or Docker mode;
- runtime owner and actual runtime root;
- credential discovery/import behavior;
- health, Agent, provider, writeback and cleanup probes;
- optional connector boundary.

Do not reproduce Compose file names, environment-variable catalogs, internal container layout, context files, locks or Jarvis Box lifecycle implementation. If the public release contract is incomplete or contradictory, block and report it to the Jarvis Box owner.

## 4. Native path

Use the released Native installer as the existing authorized OS user. The installer must reuse that user, preserve any discovered existing runtime/state and refuse an upgrade while the existing service is still running.

Before upgrade, use the released service lifecycle command to stop the service. Active Tasks must finish or be explicitly dispositioned before installation continues. The installer does not force-cancel work.

After installation, record:

- actual runtime owner and runtime root;
- release version;
- Agent and provider capability evidence;
- health/status evidence.

## 5. Docker path

Use the released Docker onboarding helper and the customer-selected absolute deployment home. Start in read-only mode. Let the helper import approved portable Host identities into the persistent runtime; do not perform a blanket Host HOME mount or credential copy.

Use the customer Jarvis Runtime Foundation through the release's generic runtime-job transport to bootstrap, sync and run its doctor. The Host Scheduler Adapter is authoritative; bootstrap and recovery must disable an in-container scheduler.

Record:

- deployment owner/home and release version;
- digest-pinned image;
- selected Host identity and capability-only import evidence;
- persistent Runtime Foundation and Agent discovery evidence;
- optional connector boundary and Docker-socket decision.

## 6. Verify the selected environment

Run the release's generic verification, then the customer Runtime Foundation doctor and a real Agent discovery probe. Complete at least one supervised happy path in the selected environment:

```text
provider or IM ingress
  → dispatcher
  → Task/Run
  → workspace when required
  → Runtime Agent
  → provider or IM writeback
  → terminal lifecycle
  → workspace and external-resource cleanup
```

Verify the exact provider identity and target. Never print tokens; capability or equality evidence is sufficient. Generic health alone is not onboarding completion.

If any probe fails, record the exact owner and recovery action. Do not patch packages or runtime state interactively and report the deployment reproducible.

## 7. Record customer-level facts

Write only stable integration facts back to Company runtime governance:

- Native or Docker mode;
- runtime owner and actual runtime root;
- release version and image digest when applicable;
- credential discovery/import boundary;
- Runtime Foundation doctor and Agent discovery;
- provider writeback and cleanup evidence;
- optional connector and host-root-equivalent capability decisions.

Use Jarvis Box's own public operations manual for commands and recovery. Do not copy its runbook, configuration catalog, Task state or internal paths.

## 8. Enter shadow

Update the onboarding work card and Construction Journal from verified evidence. The selected workflow becomes `ready-for-shadow`, not `active`.

Representative customer-supervised tasks advance `ready-for-shadow → shadowing → active`. New repository learning or self-improvement publishes a new ref; it never silently mutates the active runtime.

## Runtime Foundation scheduled jobs

不要让客户手工编写 maintenance/self-improve 或 cron。使用生成后的 `runtime-foundation/manage.py` 按 Part 4 已选择的部署模式完成首次安装或同模式升级：Native 以当前已有 OS 用户直接安装；Docker 先在持久化 Agent HOME 中执行 `install-inner`，再在宿主机以 `install --mode docker` 安装唯一 scheduler owner。只有 `status` 同时证明所选 mode、唯一 owner 和 Docker transport reachability 时才能通过 Part 4；label loaded 或配置文件存在都不是充分证据。发现另一部署模式的配置或 scheduler owner 时立即停止，不得自动切换。
