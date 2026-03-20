---
id: instinct-007
confidence: 0.5
source_count: 2
created: 2026-03-20
last_confirmed: 2026-03-20
category: coding
scope: global
---

# CI pytest Invocation & Minimalism

In Python CI workflows:
- Prefer `python -m pytest` over the `pytest` console entrypoint to avoid import-path differences across Python versions
- For CI jobs with post-failure reporting, keep the test step authoritative and use `if: always()` on downstream notification steps instead of re-implementing failure logic with `continue-on-error`
- Fetch raw CI logs early when a rerun still fails after a workflow patch, rather than inferring failure solely from job-step metadata

## Anti-pattern
DO NOT use `continue-on-error` plus custom gating when a simple `always()` on the reporting step achieves the same result with less orchestration surface.

Source: PET-13 feedback (3 CI debugging turns converging on this pattern)
