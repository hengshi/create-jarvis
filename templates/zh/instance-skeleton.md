# 实例骨架示例

```text
<company>-jarvis/
├── README.md
├── MAINTENANCE.md
├── SKILL.md
├── modules/
│   ├── <module-a>/
│   │   ├── overview.md
│   │   ├── known-issues.md
│   │   ├── decisions.md
│   │   ├── rejected-features.md
│   │   └── test-coverage.md
│   └── <module-b>/
│       └── ...
├── sources/
│   ├── <source-a>/
│   │   └── README.md
│   └── <source-b>/
│       └── README.md
├── cross-cutting/
│   ├── module-interactions.md
│   └── version-changelog.md
├── tools/
│   ├── README.md
│   └── <scripts or manuals>
├── skills/
│   └── <company-jarvis>/
│       └── SKILL.md
└── _raw/ or _exports/
    ├── README.md
    └── <optional snapshots>
```

## Notes

- 这只是一个拓扑示例，不意味着第一天每个文件夹都必须存在。
- 从第一条真实闭环所需的最小有用子集开始。
- jarvis-box 这类 runtime 调用方可能要求根目录 `SKILL.md` 作为入口 skill。保持它有效且可独立使用。
- 通过持续 回写 积累历史深度，而不是伪造成熟度。
