# Create Jarvis 的目标

客户使用自己已经授权的 Host Agent，从一句自然语言请求开始，逐步得到：

1. 客户拥有并发布在其 GitHub 或 GitLab 上的 `<company-slug>-jarvis`；
2. 各代码仓库中经真实历史 episode 验证、按客户 Git policy 交付的 repo-local skills；
3. 使用客户真实 source、角色、路由、测试、review、发布和验收方式构建的 workflow skills；
4. 加载固定 Company/repo revisions、以独立高权限身份运行的正式 jarvis-box 数字员工。

## 产品入口

客户不安装 create-jarvis，也不先安装 jarvis-box。客户只让当前 Host Agent 阅读 canonical GitHub URL 并开始建设。Agent 自己完成方法读取、版本固定、工作目录发现、任务协调和恢复。

## Construction Coordinator + 1 + 2

收到客户请求的 Host Agent 是 Construction Coordinator。它先收集可验证的授权构件，再协调两个写入边界独立的长任务：

- Company construction 建立公司级语义、能力、source、repo fleet 和路由，并发布 customer-owned Company Jarvis repo；
- Repository learning 读取真实 code changes 和完整 episode，把可复用执行知识写回所属代码仓库。

有子 Agent 时可并发；没有时由 Coordinator 按两个 RUN contract 顺序执行。并发只是效率手段，不是要求客户开两个终端的产品接口。

## 恢复而不建设状态机

两个 lane 各自维护普通 Markdown progress。Coordinator 额外维护一个只包含 pointers 的 `CONSTRUCTION-JOURNAL.md`，用于在新会话中找回 method commit、lane progress、远端交付、blocker 和下一动作。

这些文件供 Agent 阅读，不定义 parser、daemon、heartbeat 或 JSON phase 状态机。中断后再次发送同一句客户请求即可恢复。

## Repository learning 的本质

学习单位是完整、可重放的真实工作 episode，不是单个 commit，也不是 commit message 分类：

```text
visible START
  → pre-change baseline replay
  → hidden real outcome comparison
  → no_skill_gap / minimal skill delta
  → same-case rerun
  → adjacent regression
```

客户可选择最近一年、两年、全部可达历史或自定义范围。Agent 必须检查范围内 commits 的实际 code changes；只有证明行为改善的 repo-local delta 才保留。

## 从 construction 到上岗

`1+2` 不是终点。Coordinator 继续完成 reconciliation、workflow construction 和 formal runtime deployment。Workflow 按以下证据成熟：

```text
draft-template → construction-ready → runtime-deployed
               → ready-for-shadow → shadowing → active
```

没有后续真实任务时，诚实停在 `ready-for-shadow`。不能凭一次初始请求制造第三至第五天才会出现的生产证据，也不能替客户完成最终业务批准。

## 权限模型

Host Construction Agent 与正式 Jarvis Agent 都是高权限执行主体。正式 jarvis-box 容器以 root 运行，
独立 identity 用于审计、轮换和撤销，不是业务降权机制。

- Host Agent 使用客户当前明确授权的身份建设资产；
- 正式 runtime 使用独立、可审计、可轮换、可撤销的高权限身份；
- 正式身份可以按客户决定拥有超级管理员能力；
- 人类 Host home、SSH Agent 和凭据不会被整体复制进正式 runtime；
- Docker socket 等价于宿主机 root 能力，只有客户明确授权才启用；
- IM provider 原生凭据只属于 connector。

## 最终客户体验

客户只参与无法从证据判断的业务选择、授权 checkpoint、Git review/approval 和真实 shadow 验收。客户不需要理解 Phase、cursor、oracle、baseline、eval、内部 progress 文件或 runtime 安装细节。
