# Rollout 确认清单

在把一个生成出来的 JARVIS 称为 试点-ready 之前，使用这份清单。

## 已由 humans 确认的 truth

- [ ] business intent 已确认
- [ ] 第一条有价值闭环已确认
- [ ] shadow-pilot success criteria 已确认
- [ ] 纳入的 sources 已确认
- [ ] 纳入的 repos 已确认
- [ ] 纳入的 workflows 已确认
- [ ] ownership assignments 已确认
- [ ] 权威来源 locations 已确认
- [ ] writeback policy 已确认

## Runtime 边界

- [ ] runtime owner 是 jarvis-box 或其他明确 runtime，不是 create-jarvis-skill
- [ ] `JARVIS_HOME` / generated instance root 已确认
- [ ] `JARVIS_TARGET_HOME` 可写，或 unresolved 已写入 `bootstrap-result.json`
- [ ] `JARVIS_BOX_HOME` 如果存在，只被当作 runtime host root
- [ ] runtime install/setup/service/webhook responsibilities 不属于这个 instance scaffold
- [ ] secret values 没有写入生成产物
- [ ] noninteractive missing inputs 被记录为 unresolved，而不是猜测填充

## 生成结构的质量

- [ ] 占位符足够明确
- [ ] 稳定入口存在
- [ ] 需要时已体现 source / repo / workflow 各层
- [ ] central JARVIS 是 router，不是 content mirror
- [ ] repo-local truth 留在 repos
- [ ] source skills 负责 route/interpret sources，不 dump source content
- [ ] maintenance guidance 存在
- [ ] 回写 expectations 存在
- [ ] calibration 和 `no_skill_gap` expectations 存在

## 成熟度诚实性

- [ ] 没有把虚假历史伪装成真实知识
- [ ] 没有把占位 owner 写成真实 owner
- [ ] 没有把猜测出来的 workflow 写成已验证的公司流程
- [ ] 试点 scope 小于“覆盖全公司”的梦想
- [ ] 真实 loop 跑通前，结果只能叫 pilot-ready，不能叫 pilot-proven
