---
id: instinct-002
confidence: 0.8
source_count: 5
created: 2026-03-18
last_confirmed: 2026-03-18
category: process
scope: global
---

# Durable Handoff Artifacts

When external workflow tooling (e.g. Linear API) is unavailable:
- Keep a single repo-local handoff note with PR URL, branch head, and validation caveats
- Use stable references (PR URLs, branch heads) instead of "latest commit" fields
- Include exact comment text and state-change payloads, not just prose instructions
- Avoid self-invalidating metadata that needs refresh after every commit

Source: PET-8 feedback (repeated across 8+ continuation turns)
