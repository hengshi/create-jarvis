# 反模式

## 1. 漂亮外壳
生成一个外观精致的 JARVIS repo，却没有澄清业务意图、第一条闭环或下一批 owners。

**更好的做法：** 先定义第一条有价值的闭环，再只生成真正支撑它的内容。

## 2. 内容倾倒
把源文档、issue 正文或会议记录直接复制进 JARVIS。

**更好的做法：** 提炼模式、路由线索和可持续复用的摘要。

## 3. 一切都集中化
把 repo 内事实 一股脑塞进中心 JARVIS repo。

**更好的做法：** 把 repo-local execution guidance 留在 repo 内，由 JARVIS 负责路由过去。

## 4. 占位符表演
保留一些看起来像已验证公司事实的占位符。

**更好的做法：** 明确标记占位符，并写出预期由谁负责替换。

## 5. 在证明价值前追求穷尽性
在证明第一条有用闭环之前，就试图映射每一个 source、repo 和 workflow。

**更好的做法：** 从能体现复利价值的最小范围开始。

## 6. 单英雄设计
假设一个人或一个 agent 就能独自构建并维护 JARVIS。

**更好的做法：** 尽早定义 ownership 和 handoff。

## 7. 静态心态
把第一版 scaffold 当成已经完成的 JARVIS。

**更好的做法：** 把 first pass 当作 rollout 的一个阶段发布，并附带 backlog 与后续步骤。

## 8. Skill 膨胀
每次失败或每个想法都新建 skill。

**更好的做法：** 先检查 `no_skill_gap`，默认合并到已有 skill，并要求证据支撑 skill growth。

## 9. 过早 upstream
把公司私有 facts、examples、repo names 或 issue IDs 移进通用 create-jarvis-skill 方法论。

**更好的做法：** 只有在脱敏且证明可复用后，才提升 company-neutral method。

## 10. Template 污染
因为一个内部 pilot 更清楚，就把私有例子放进通用模板。

**更好的做法：** template 保持抽象；私有例子留在 company instance 或 repo-local skill。

## 11. Runtime 接管
要求 create-jarvis-skill 管理 install、credentials、webhooks、task queues 或 service lifecycle。

**更好的做法：** runtime mechanics 留给 jarvis-box 或调用方 runtime；本仓库聚焦 methodology、scaffold、pilot 和 calibration。
