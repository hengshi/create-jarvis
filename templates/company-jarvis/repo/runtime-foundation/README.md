# Runtime Foundation

这里保存 {{COMPANY_NAME}} 自己拥有的稳定 Runtime Jobs。它们随 Company Jarvis 一起生成和版本化，不由运行时 Agent 临时编写。

## 唯一运行模型

| 部署模式 | scheduler owner | 执行路径 |
|---|---|---|
| Native | 当前 OS 用户的 launchd/crontab | scheduler -> `jarvis-maintenance` / `jarvis-self-improve` |
| Docker | 宿主机 launchd/crontab | scheduler -> Jarvis Box `runtime-job` -> 容器内同一个 inner job |

容器内不运行第二套 scheduler。部署模式在正式部署时确定；之后只允许同模式升级。发现另一模式的 scheduler owner 或配置残留时，安装会直接失败，不会替客户自动切换部署模式。`status` 只有在 owner 唯一且 Docker transport 可达时才返回 `healthy: true`。

## create-jarvis 应如何安装

正式部署阶段的 Runtime Agent 负责执行这些命令，客户只选择 Native 或 Docker，不需要自己拼命令。

Native：

```bash
python3 runtime-foundation/manage.py install \
  --mode native \
  --root "$HOME/.{{COMPANY_SLUG}}-jarvis" \
  --company-repo <当前 Company Jarvis Git remote>
```

Docker 分两步。先在持久化 Agent HOME 所在容器里安装 inner jobs，且不安装容器 scheduler：

```bash
python3 runtime-foundation/manage.py install-inner \
  --root /root/.{{COMPANY_SLUG}}-jarvis \
  --company-repo <当前 Company Jarvis Git remote>
```

再在宿主机安装唯一 scheduler adapter：

```bash
python3 runtime-foundation/manage.py install \
  --mode docker \
  --root "$HOME/.{{COMPANY_SLUG}}-jarvis" \
  --company-repo <当前 Company Jarvis Git remote> \
  --release-helper <Jarvis Box 固定版本 release helper 的绝对路径> \
  --deployment-home <Jarvis Box deployment home 的绝对路径> \
  --container-root /root/.{{COMPANY_SLUG}}-jarvis
```

`runtime-foundation.json` 不保存 Token。Native 继承安装 Jarvis 的当前 OS 用户认证；Docker 继承导入到持久化 Agent HOME 的认证。

## 运维入口

```bash
"$HOME/.{{COMPANY_SLUG}}-jarvis/bin/jarvis-runtime-foundation" status \
  --root "$HOME/.{{COMPANY_SLUG}}-jarvis"
```

默认在工作日 10:30 执行 maintenance、18:30 执行 self-improve；Coordinator 可以在安装时通过 `--maintenance-cron` 和 `--self-improve-cron` 明确覆盖。`stop` 只停止当前已选模式的 scheduler，不会启用另一模式。日志、锁和临时 workspace 全部位于安装时选择的 Runtime Foundation root，不依赖任何公司专属的预设路径。
