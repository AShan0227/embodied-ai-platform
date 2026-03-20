---
id: instinct-003
confidence: 0.9
source_count: 4
created: 2026-03-18
last_confirmed: 2026-03-20
category: coding
scope: project
---

# CLI Subprocess Testing

For small CLI tasks:
- Implement argument validation via custom argparse types
- Test CLI through subprocess (not direct function calls) so validation, stdout format, and exit codes stay covered together
- Always use `python3 -m pytest` instead of bare `pytest` (may not be on PATH; also avoids import-path differences on newer Python versions like 3.14)
- Create `.task-estimate.md` before implementation, even when historical baseline is empty
- For network-checking CLIs, use stdlib HTTP primitives and make tests deterministic with tiny local HTTP servers rather than live internet calls

Source: PET-9 feedback, PET-13 (explicit confirmation ×2), PET-14 (confirmed + extended with network fixture pattern)
