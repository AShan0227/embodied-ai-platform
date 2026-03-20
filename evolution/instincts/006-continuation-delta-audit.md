---
id: instinct-006
confidence: 0.5
source_count: 2
created: 2026-03-20
last_confirmed: 2026-03-20
category: process
scope: global
---

# Continuation Delta Audit

When a task continues across multiple turns:
- Begin each continuation with a delta audit: last commit scope, working tree state, external artifact status
- Stop immediately if all repo-local acceptance criteria are already met
- Define an explicit stop condition once the repo is clean, PR is open, and remaining blockers are outside the environment
- Avoid repeated "is there anything left?" audits that produce no new work

## Anti-pattern
DO NOT continue making speculative edits when the remaining blocker is external (e.g. missing tooling access).
DO NOT enter diminishing-return continuation without a clear new signal to act on.

Source: PET-8 feedback (observed across 14 continuation turns)
