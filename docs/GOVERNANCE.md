# Governance Rules

## Decision Authority

| Action | Authority | Notes |
|--------|-----------|-------|
| Strategic direction | Board (human) | Final say on all strategy |
| New agent creation | Board approval required | `requireBoardApprovalForNewAgents: true` |
| Budget increase | Board | Per-agent or company-wide |
| Goal changes (L1+) | Board | L0 refinements can be CTO-approved |
| Linear issue creation | CEO / CTO self-approve | Within approved goals |
| Architecture decisions | CTO self-approve | Within approved goals |
| Code merge | Human Review gate | Symphony enforces this |
| Instinct curation | CTO | Weekly, no Board approval needed |
| Instinct → proven pattern promotion | CTO | When confidence ≥ 0.9, source_count ≥ 5 |
| Skill draft → production skill | CTO + Board | Board reviews CTO's recommendation |
| SOUL.md changes | CTO proposes → Board approves | Never self-modify |
| Memory write (own namespace) | Auto-approve | Agent private memory |
| Memory read (allowed namespace) | Auto-approve | Per access rules |
| External communications (email/tweet/post) | Board approval required | Nothing leaves the machine without human OK |

## Budget Allocation (Monthly)

| Agent | Budget | Role |
|-------|--------|------|
| CEO | $100 | Strategy, reviews |
| CTO | $150 | Architecture, bridge, evolution custodian |
| A (Algorithm) | $150 | Coding (Codex) |
| B (Systems) | $120 | Engineering (Gemini) |
| C (Innovation) | $100 | Research |
| D (Safety) | $100 | Safety review |
| E (Product) | $100 | Product management |
| F (Hardware) | $100 | Hardware engineering (Codex) |
| G (BD) | $100 | Business development |
| S (Intelligence) | $80 | Market intelligence |
| **Company total** | $500 | |

## Human Gates

Symphony enforces these pause points:

1. **Human Review**: After Codex completes coding, before merge
2. **Board Review**: For strategic decisions in Paperclip
3. **SOUL.md Changes**: CTO proposes, Board must explicitly approve

## Cost Awareness Rules

- If agent's remaining monthly budget < 20%: notify Board, pause non-critical work
- If company monthly spend > 80%: all agents enter "essential only" mode
- Prefer fewer well-scoped tasks over many small ones
- Use cheaper models for sub-agent work when possible

## SOUL.md Self-Modification Protocol

Agents **DO NOT** directly edit their own SOUL.md. The process:

```
Agent detects own weakness (e.g., consistently low scores)
  → Writes SOUL_CHANGE_PROPOSAL to evolution/feedback/:
    "Proposed SOUL.md addition for [agent]: [specific change]"
  → CTO reviews in weekly curation cycle
  → CTO writes proposed diff to evolution/retrospectives/
  → Board approves or rejects
  → If approved, CTO applies change
  → Agent gets updated config on next heartbeat
```

## Escalation Path

```
Agent stuck → comment on issue → Human Review
CTO disagrees with CEO → Paperclip discussion → Board decides
Budget overrun → auto-pause + Board notification
Security concern → immediate pause + Board alert
```
