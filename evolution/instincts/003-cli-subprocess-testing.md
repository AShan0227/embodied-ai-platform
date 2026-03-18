---
id: instinct-003
confidence: 0.7
source_count: 2
created: 2026-03-18
last_confirmed: 2026-03-18
category: coding
scope: project
---

# CLI Subprocess Testing

For small CLI tasks:
- Implement argument validation via custom argparse types
- Test CLI through subprocess (not direct function calls) so validation, stdout format, and exit codes stay covered together
- Always use `python3 -m pytest` instead of bare `pytest` (may not be on PATH)
- Create `.task-estimate.md` before implementation, even when historical baseline is empty

Source: PET-9 feedback
