# Instance Skeleton Example

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

- This is a topology example, not a claim that every folder must exist on day one.
- Start with the smallest useful subset for the first real loop.
- Runtime callers such as jarvis-box may require a root `SKILL.md` as the entry skill. Keep it valid and self-contained.
- Add historical depth through continued writeback rather than generating fake maturity.
