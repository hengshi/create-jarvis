# Source Routing：从 Company Sources 提取 PRD 事实

此文件定义 agent 在评审 PRD/spec 时如何从 company sources 中获取事实、产品契约、执行 route 与验证 route。不预设任何固定的 source 类型、工具、技术层或组织结构。

## 核心原则

1. **agent 先查，不推回**：凡可通过已有 source 回答的问题，agent 必须自行查找。仅在所有可查 source 穷尽后，才能将问题列为 blocking question。
2. **证据优于推测**：输出中不得出现未经 source 证实的 repo、branch、path、tool、command 或 endpoint。
3. **多 source 交叉验证**：当同一事实在多个 source 中出现矛盾时，显式标注矛盾而非静默选择一个。

## 查找流程

### 1. 从 PRD 陈述追溯到 source

对 PRD 中的每个关键陈述，按以下路径追溯：

- **声明了某种现有能力？** → 查 capability map、现有契约、历史 decision record。
- **引用了某个产品行为？** → 查已发布的产品文档、spec、用户可见行为定义。
- **假设了某种交付方式？** → 查 `{{COMPANY_SLUG}}-jarvis/references/capability-delivery-surfaces.md` 确认 ownership 和 delivery surface。
- **涉及跨模块影响？** → 查 `{{COMPANY_SLUG}}-jarvis/references/jarvis-first-routing.md` 确定影响范围和 route。

### 2. 确定证据来源类型

根据 PRD 内容，从以下通用类别中选取适用的 source（不要求每类都查，不限制仅查这些）：

- **产品契约**：已发布的行为定义、接口契约、数据语义约定。
- **历史决策**：过往的 decision record、issue 结论、tradeoff 记录。
- **现有能力**：已实现的功能清单、capability map、模块边界定义。
- **质量与约束**：测试用例、已知边界条件、性能约束、兼容性要求。
- **交付上下文**：与交付相关的环境约束、发布节奏、配置差异。

### 3. 按 company routing 定位具体 source

具体到哪里查、怎么查，由 company routing 和对应 source route 决定，不由本文件硬编码。先完成 runtime quick preflight，再从 `{{COMPANY_SLUG}}-jarvis/references/jarvis-first-routing.md` 进入具体 source。

## 查证深度判断

- **material 事实**（会影响 scope / acceptance / route）：必须查到可追溯的 source 或 authority decision。
- **context 事实**（辅助理解但不改变决策）：记录来源，不强制穷尽。
- **trivial 事实**（对评审结论无影响）：跳过。

## 矛盾处理

当多个 source 对同一事实有不同结论时：
1. 在评审日志中显式列出矛盾的 source 和各自的主张。
2. 标注哪个 source 按 company governance 具有更高 authority。
3. 若 authority 层级也无法判定，升级为 blocking question。

## 穷尽声明

当某个事实在所有已知 source 中均无法找到时：
- 列出已查过的 source 清单。
- 声明为什么这些 source 应包含但未包含该事实。
- 形成 blocking question，指明需要谁来提供该事实。
