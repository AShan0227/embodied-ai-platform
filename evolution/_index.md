# Evolution System — L0 Index

> Manual-maintained index. Every instinct gets a one-line entry here.
> Agents: read this file FIRST at task start. Only load full instinct files (L2) when a title matches your task context.

## Active Instincts

| File | Confidence | Category | One-line summary |
|------|-----------|----------|-----------------|
| 001-strategy-synthesis-frame.md | 0.7 | process | 战略研究用固定框架：信号扫描→共性约束→元范式→董事会影响 |
| 002-durable-handoff-artifacts.md | 0.9 ⭐ | process | 交接文档用稳定引用（PR URL/branch head），避免自失效元数据 |
| 003-cli-subprocess-testing.md | 0.9 ⭐ | coding | CLI 任务用 subprocess 测试覆盖验证/输出/退出码，含网络 CLI fixture 模式 |
| 004-pair-recommendations-antipatterns.md | 0.6 | process | 战略建议配反模式表，附来源可审计地图 |
| 005-ci-file-based-guards.md | 0.6 | process | CI 用文件状态替代 step output，避免 continue-on-error 语义歧义 |
| 006-continuation-delta-audit.md | 0.5 | process | 多轮续接先做增量审计，满足验收即停，不做投机性编辑 |
| 007-ci-pytest-invocation.md | 0.5 | coding | CI 用 python -m pytest，报告步骤用 always()，早拉原始日志 |

## Promoted to Proven Patterns

| File | Promoted | Reason |
|------|----------|--------|
| 002-durable-handoff-artifacts.md | 2026-03-20 | confidence 0.9, source_count 8, confirmed across PET-8 (14 turns) |

## Recently Archived

| File | Reason | Date |
|------|--------|------|
| *(none)* |

## Stats

- Total active instincts: 7
- Total archived: 0
- Total promoted: 1
- Last curation: 2026-03-20 (Friday, automated weekly)
- Next curation: 2026-03-27 (Friday, automated)
