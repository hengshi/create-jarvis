# Repo-Local Skill 模板

规范的 10 文件 package，为单个仓库提供 agentic skill。每个文件有单一职责；合在一起构成完整的引导、验证和自我改进循环。

## 规范结构

```
repo-local-skill/
  README.md                         ← 本文件
  skills/
    SKILL.md                        ← 仓库入口：任务路由、工作规则、边界
    eval-loop.md                    ← 评估循环方法
    code-review/
      SKILL.md                      ← 仓库代码审查门
      scripts/
        precheck.sh                 ← 自包含的骨架合同与环境线索检查
    references/
      source-of-truth.md            ← 产品行为事实、API 合约、配置假设
      architecture-map.md           ← 模块布局、扩展点、风险区域
      test-entrypoints.md           ← 冒烟、单元、集成、lint 命令
      runtime-and-testability.md    ← 本地开发环境、日志、依赖、禁止操作
      history-replay-loop.md        ← 历史回放规范
    self-skills-improve/
      SKILL.md                      ← 自我校准：何时增长 skill pack
```

## 使用方式

canonical 10 文件是 Phase 8 的**确定性起点**，不是成熟度上限。Phase 8 必须立刻用每个 repo 的真实证据填充核心文件：将所有 `BOOTSTRAP_REQUIRED` sentinel 替换为可观察事实。占位符不是"完成"——Phase 8 必须填充，不可将 sentinel 视为长期状态。

特别是 `skills/code-review/SKILL.md` 的“仓库特有检查”表：如果扫描代码、配置、CI、测试和历史后没有观察到额外 trigger，也必须替换 sentinel 为明确的 `not-observed` 记录，并写出实际扫描范围和 pointer；不能凭通用常识补造检查，也不能原样保留 sentinel。

专业 reference 后续只能由真实任务、pilot 或 history replay 生长，不设任意数量阈值。

## Token

repo-local 模板唯一可渲染 token 是 `{{REPO_NAME}}`。不得新增其他 token、reference company 名称或私有路径、假 repo/命令/技术栈。默认分支、owner、公司 handoff 和技术栈都由 Phase 8 从目标 repo 与 company Jarvis evidence 填写，不由 instantiator 猜测。

## 不覆盖的范围

- **跨仓库工作流协调**——由 company JARVIS skills 处理。
- **通用方法论**——create-jarvis-skill 上游规则处理通用 skill 创建模式。
- **组织级 rollout**——团队级别采用和 ownership 属于公司层面。

## 前置条件

- `SKILL.md` 必须可被 skill loader 加载（YAML frontmatter，有效 Markdown）。
- `precheck.sh` 必须可执行（`chmod +x`）。它只检查 repo/canonical package 合同并报告环境线索，不执行产品 build/test。刚实例化但尚未填充的骨架应退出非 0；Phase 8 填充完成且不存在核心文件缺失、临时占位、未渲染 token 或硬编码机器私有路径时才退出 0。缺技术栈工具只报告 `WARN`。
- References 不能包含公司专有 secret 或凭据。
