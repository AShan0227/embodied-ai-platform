---
id: instinct-005
confidence: 0.6
source_count: 1
created: 2026-03-18
last_confirmed: 2026-03-18
category: process
scope: project
---

# CI File-Based Guards over Step Outputs

In GitHub Actions workflows with `continue-on-error` steps:
- Use file-backed exit codes for guard conditions instead of step `outcome`/`conclusion` semantics
- Step-context evaluation can be inconsistent when `continue-on-error` is involved
- Write an explicit status output file and key later comment/fail logic off that file

Source: PET-13 feedback (CI debugging across 3 continuation turns)
