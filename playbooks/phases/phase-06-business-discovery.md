# Phase 6 - 业务发现和生成策略

目标：在写文件前，从客户授权范围内建立完整的公司 Jarvis 生态蓝图。这个蓝图必须能支撑 Phase 7 生成接近 `hengshi-jarvis` 形态的客户 repo，而不是只列几个仓库或工程层。

Phase 6 是同一个 Phase 内的两层扫描，不是两个独立 phase：

1. **全生态拓扑扫描**：覆盖所有已授权 repos、docs、tests、issues-or-history、CI 配置、客户材料。目标是识别 company product surfaces、完整 module candidates、repo roles、sources、workflow scope。不要求把每个模块写成熟。
2. **第一条 workflow 深挖**：对 first workflow 的 modules、repos、sources 做足够深的 evidence extraction，保证 Phase 7/8/9 和 Phase 11 可执行。

## 步骤

### 第一层：全生态拓扑扫描

1. 明确允许读取的全部授权材料范围：docs、repos、tests、issues、tickets、wiki、CI 配置、客户产品材料。
2. 提炼 domain vocabulary、product surfaces、user roles、workflow gates、repo-to-capability hints。
3. 提炼 identity signals：source/repo/docs 中出现的 product、brand、company、package namespace、artifact name。
4. 对照 Phase 4 的 company/product identity，形成 identity reconciliation。source-detected identity 与客户声明身份不一致时，只能标记为 `source-detected` / `needs-owner-confirmation` / `conflict`，不能混写成已确认主体。
5. 形成 product/domain module candidates，每个 candidate 必须有 evidence pointer、confidence 和 confirmation status。
   - 如果 Phase 4 提供了 confirmed module hints，这些值默认就是目标 `modules/<module>/` 目录名；为每个 hint 生成 coverage matrix：`included`、`deferred-needs-evidence` 或 `rejected-by-owner`。
   - **confirmed module hint 只确认输出命名空间/名称，不证明模块的业务含义、owner、实现或 `included` 状态。** 名称确认后仍需完整的语义证据链。
   - agent 不能自行把 confirmed module hint 改名、改大小写、合并或翻译成通用 BI taxonomy。若认为名称不合理，保留原目录名，在 `overview.md` 写 alias / suspected merge note，并把 owner confirmation 放入 unresolved map。
   - 只有客户/operator 明确要求改名时，才能产生 renamed output；此时原 hint 仍要在 coverage matrix 中可追踪。
   - 不能只输出最容易从 repo 猜到的少量模块，让 confirmed module hints 消失。
6. 为每个 module candidate 连接 sources、repos、tests/issues 和已知 workflow role。
7. 明确哪些 repo-local skills 必须生成，哪些 source/workflow skills 必须生成，哪些进入 backlog。
   - 如果 Phase 4 提供了 confirmed workflow scope，这些值默认就是目标 `skills/<workflow>/SKILL.md` 名；为每个 workflow 写 `create-now` 或 `create-scaffold-needs-pilot`，不要改名或合并。
   - 如果 Phase 4 提供了 confirmed source scope，这些值默认就是目标 `sources/<source>/README.md` 路由名；为每个 source 写 `route-created`、`needs-access` 或 `raw-export-boundary`，不要改写成泛化来源名。
8. 区分 `confirmed`、`needs-owner-confirmation`、`grow-from-pilot`、`grow-from-history-replay`。
9. 选择需要使用的 `templates/` 文件。

### 第二层：第一条 workflow 深挖

10. 对 first workflow 涉及的 modules、repos、sources 执行足够深的 evidence extraction：
    - 实际读取 repo 代码目录、build files、CI 配置、测试入口、现有 agent guidance、相关 docs；
    - 记录具体 endpoint、route、label、方法/字段名、版本号、文件/测试数量、build/test 命令；
    - 确认每个 pilot repo 在 first workflow 中的角色和验证入口。
11. 对非 first-workflow 的已确认 source，如果当前环境暂不可访问，标记为 `deferred-needs-access`，不阻断 bootstrap；只有 first workflow 必需 access 才在 Phase 5/6 阻断。

### 证据包写入

12. 在目标 repo 的 `_bootstrap/discovery/` 写入以下 Phase 6 证据包（保持现有 5 个文件，不新增 claim-ledger 之类文件）：
    - `evidence-inventory.md`：实际读取过的 source/repo/path、执行的检索命令、正向发现和负向检索结果；
    - `module-coverage-matrix.md`：每个 confirmed hint / discovered module 的状态、业务角色、具体 evidence pointer、repo/test/issue 关联和 first workflow role；
    - `repo-role-map.md`：每个 pilot repo 的业务职责、技术边界、repo-local handoff 和验证入口；
    - `workflow-map.md`：first workflow 的 START -> WORK -> VERIFY -> END，以及每一步使用的 module/source/repo；
    - `generation-plan.md`：Phase 7-9 要创建什么、哪些事实仍待 owner/权限、哪些内容禁止生成。
13. 只有证据包满足下面的 Phase 7 入口门，才进入 Phase 7。

## 证据优先的语义发现规则

Phase 6 的核心产出不是目录名称列表，而是每个模块、source、repo 角色的可验证业务语义。以下规则防止浅层扫描和语义错误。

### 搜索顺序：先读高信号地图，再搜原始代码

在搜索原始代码之前，优先读取已有客户高信号材料（如果存在）：

1. 产品文档和导航结构
2. UI 标签和路由
3. 测试/规约文件名和入口
4. CLI help 输出
5. README、AGENTS.md、CLAUDE.md 等已有 agent guidance
6. issue/历史词汇
7. 已有知识地图

这些材料中的术语、路由、模块名直接反映客户业务语义，是最高信号来源。

### 模块发现与消歧

- 对每个 hinted/discovered module，从客户词汇构造别名（中文名、英文名、缩写、代码中的 package/namespace 变体），在所有相关 repo/source 中递归搜索。仅靠精确英文 token 搜索不够。
- 显式拒绝/消歧同名异义和近似匹配。记录为什么一个看似合理的代码匹配不是目标业务概念。例如：相同的 `market` 词根可能分别指外部云市场订阅和客户产品内的应用/模板市场；如果产品文档和 UI 路由指向不同概念，必须在 evidence inventory 中明确区分。
- 如果仅存在间接证据（仅依赖声明、路径存在、同名不同义），使用 `deferred-needs-evidence`；不要为了满足预期目录列表而强行标 `included`。

### `included` 模块的双锚点要求

一个模块标 `included` 必须同时满足两个锚点：

1. **产品身份锚点**：证明客户面向/业务能力的存在——产品文档、UI 标签/路由、验收/E2E 测试、CLI 表面、issue 分类法，或 owner 已确认的 artifact。
2. **实现/验证锚点**：证明该能力在哪里实现或测试——`<repo-name>:<repo-relative-path>` 指向真实存在的代码、测试、构建配置或 CI 文件。

**路径存在或依赖声明本身不能单独证明业务含义。** 必须读取匹配内容，确认其语义与模块的业务定义一致。

### 负向搜索有效性

负向搜索只有在以下条件下才有效：

- 已用别名覆盖（中文名、英文名、缩写、代码变体）
- 已在 repo role map 中命名的所有 repo 内递归搜索产品文档、UI、测试、历史
- 搜索范围记录在 evidence inventory 中

未满足以上条件的负向搜索结果不能作为"该模块不存在"的结论。

### 检索命令精度

evidence inventory 中每一条检索命令必须精确且在当前 checkout 上下文中可直接执行：

- 禁止 `...`、Unicode 省略号、虚构的伪路径、未测量的 `N+` 计数
- 精确数量/版本/命令必须有产生该结果的命令输出或指针
- 禁止"按常见 REST 习惯补全"未观察到的 endpoint/route/字段

### Source Route 全映射

每个可访问的 source route 必须在发现阶段完成映射：

- source 类型
- 具体 repo/doc 指针
- 访问方式
- 搜索方法
- 新鲜度/分支证据
- 状态（`mapped`、`deferred-needs-access`、`blocked`）

只有真正不可访问的 source 才能保持 deferred。可读但未映射的 source route 不能在 Phase 7 保留 `needs-evidence` 或模板占位。

### Phase 7 入口门补充规则

Phase 7 入口门原有规则不变，新增以下补充：

- 当一个模块只有同名异义匹配/间接锚点时，Phase 7 入口门必须把发现发回 Phase 6 继续扫描
- 当一个可访问 source 仍为泛化状态时，Phase 7 入口门必须发回 Phase 6 补全 source route 映射

## Evidence Inventory 精度规则

- 每条精确 endpoint、route、label、方法、字段、版本、数量、命令必须记录：
  - observed fact（实际看到的值）；
  - repo-relative pointer（哪个 repo、哪个文件、哪一行或哪个命令输出）；
  - retrieval/check（用什么命令或读取方式获得的）。
- repo-relative pointer 统一使用可解析格式 `<repo-name>:<repo-relative-path>`，并且该路径必须在当前授权 checkout 中真实存在。只写 repo 名、`service/` 这类泛化顶层目录、`model/ + service/` 或 bootstrap 机器绝对路径不算具体证据。
- 正式文件（modules/、sources/、skills/、references/）只能引用 evidence inventory 中已有的事实。
- 无证据时省略精确值或标 `needs-verification`。
- 禁止"按常见 REST 习惯补全"——没有在客户材料中实际观察到的 endpoint/route/字段不得出现在正式文件中。

## Phase 7 入口门

Phase 6 不是"读过一些文件"就完成。进入 Phase 7 前必须同时满足：

- `_bootstrap/discovery/` 的五个文件已经存在且非空。
- 对当前环境中可访问的客户 repo/source 已实际执行扫描；不能把本地可读材料写成 `needs-access` 或"待 Phase 6 扫描"。
- 每个 `included` module 至少有一个可解析且真实存在的 `<repo-name>:<repo-relative-path>` 客户 evidence pointer，以及它在 first workflow 或产品中的明确角色。`JARVIS_MODULE_HINTS` 只能确认名称，不能单独充当业务证据。
- 如果某个 confirmed module 暂时没有正向证据，coverage matrix 必须记录实际搜索过的 repo/path/query 和负向结果，并标成 `deferred-needs-evidence`；不能复制一段通用 `needs-evidence` 文本后标 `included`。
- repo role map 必须来自 repo 内的 build files、CI、代码目录、测试目录、现有 agent guidance 或文档证据，不能只写语言/框架猜测。
- generation plan 明确引用 coverage matrix、repo role map 和 workflow map。
- endpoint、URL route、issue label、方法/字段名、工具版本、文件/测试数量、build/test command 等精确事实，必须在 evidence inventory 中有实际读取命令和 pointer；没有证据时写 `needs-verification`，不能由模型补全。
- `_bootstrap/discovery/` 可以记录本次机器的扫描路径；Phase 7 的 durable files 只能使用 repo 名 + repo-relative path 或配置变量，不能保留 `/e2e/customer-repos` 这类测试机绝对路径。
- 非 first-workflow 的已确认 source 暂不可访问时，标 `deferred-needs-access`，不阻断 Phase 7 入口；只有 first workflow 必需 access 缺失才阻断。

任何 module 文件中出现"待 Phase 6 扫描/补充"，都证明 Phase 6 被越过；Phase 6 和 Phase 7 都不能标 `completed`。

当客户 repo 可读时，每个 `included` module 在进入 Phase 10 前必须已经有 evidence-backed、module-specific 的首跳路由、first proof、false owner 和搜索/验证入口。shadow pilot/history replay 用来校准，不是用来填基本路由。不得用"本模块相关问题""首次 pilot 后填充""本模块尚未通过 pilot"等批量通用段落。

每条 evidence pointer 必须是完整 `<repo>:<repo-relative-path>` 格式，不含 `...`、Unicode 省略号、glob 或说明性后缀。指向文件或目录均可，但必须在授权 checkout 中存在。允许真实存在的目录作为 pointer。不能因为同一 module 有一条合法 pointer，就放过其他伪 pointer。

## 生态蓝图必须包含

- product/domain modules，不用通用工程层充当主要 modules。
- source map：docs、repos、tests、issues/tickets/wiki 等来源的访问方式和边界。
- module coverage matrix：每个 confirmed module hint 和每个 evidence-discovered module 的 included/deferred/rejected-by-owner 决策；confirmed 名称默认原样输出。
- repo role map：每个 pilot repo 在 first workflow 中做什么。
- workflow map：first workflow 的 START -> WORK -> VERIFY -> END。
- skill map：company entry、repo-local、source、workflow skills 的创建或 backlog 决策。
- unresolved map：缺哪些 owner、权限、证据或确认。
- identity reconciliation：客户 company identity、客户确认的 product identity、source-detected identities、冲突和 owner confirmation 状态。

## 禁止

- 不做 raw source dump。
- 不生成没有 evidence pointer 的成熟 module。
- 不把 `backend` / `frontend` / `api` 这类工程层当作主要业务 module。
- 不把 templates 的结构当作客户事实。
- 不把 source-detected product/brand identity 直接并入客户 company identity。
- 不把 pilot scope 扩成全公司扫描——全生态拓扑扫描仍以已授权范围为界。
- 不把客户确认的 module/source/workflow 名称翻译、缩写、合并或改写成 agent 自己喜欢的分类名。
- 不先批量生成通用 module，再把真实客户扫描推迟到 Phase 8 或 Phase 11。
- 不用相同的通用 source-of-truth、关键概念、接口和验证段落填满所有 modules。
- 不根据领域常识编造 API endpoint、UI route、issue label、owner、测试数量或 CI 行为。

## 读物

- `GOAL.md`
- `acceptance.md`
- `playbooks/phase-checklist.md`
- `templates/`
