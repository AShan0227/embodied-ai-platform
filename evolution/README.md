# Evolution System

The company's learning backbone. Four loops, four speeds.

> Format spec adapted from [ECC Continuous Learning v2.1](https://github.com/affaan-m/everything-claude-code) — instinct-based architecture with confidence scoring, domain tagging, and scope awareness.

## Directory Structure

```
evolution/
├── _index.md              ← L0 index: one-line summary of every instinct (read first!)
├── feedback/              ← Loop 1: raw signals from every completed task
│   └── {date}.md
├── instincts/             ← Loop 2: compressed patterns extracted from feedback
│   ├── {instinct-name}.md
│   └── archived/          ← instincts with confidence < 0.3
├── metrics/               ← Loop 1: agent self-scores per task
│   └── {agent-id}/
│       └── {issue-id}.md
├── skill-drafts/          ← Loop 3: new skill proposals from agents
│   └── {skill-name}.md
└── retrospectives/        ← Loop 4: monthly summaries + SOUL.md change proposals
    └── {YYYY-MM}.md
```

## Loop Schedule

| Loop | Frequency | Owner | Action |
|------|-----------|-------|--------|
| 1. Task Feedback | Every task | All agents | Write feedback + self-scores |
| 2. Instinct Curation | Weekly (Friday) | CTO | Extract patterns, update confidence |
| 3. Skill Creation | Bi-weekly | CTO | Review drafts, promote to skills/ |
| 4. Self-Improvement | Monthly | CTO + Board | Retrospective, SOUL.md proposals |

## Instinct File Format (ECC v2.1 Compatible)

Each instinct is **atomic** — one trigger, one action. File format uses YAML frontmatter:

```yaml
---
id: prefer-explicit-error-handling    # kebab-case unique identifier
trigger: "when implementing error handling in new modules"
confidence: 0.7                       # 0.0–1.0 (see scoring rules below)
domain: coding                        # coding | architecture | process | communication | security | testing
scope: global                         # global (all projects) | project (single project)
source: task-feedback                 # task-feedback | observation | imported | manual
source_count: 3                       # independent observations supporting this
created: 2026-03-15
last_confirmed: 2026-03-15
---
# Instinct: Prefer Explicit Error Handling

## Pattern
When implementing error handling in new modules — especially API integrations
and file I/O operations.

## Action
Always use explicit error types rather than generic try/catch. Define custom
error classes for each failure mode. Return structured error objects with
context (what failed, why, what to try next).

## Evidence
- PET-12: Generic try/catch hid a rate-limit error, causing 2h debugging
- PET-18: Explicit error types caught a config issue immediately
- PET-23: Custom errors enabled automatic retry logic

## Anti-pattern
DO NOT use bare `except Exception` or `catch (e)` without re-typing.
DO NOT swallow errors silently.
```

### Properties (from ECC)
- **Atomic**: one trigger, one action — no compound instincts
- **Confidence-weighted**: 0.3 = tentative, 0.5 = moderate, 0.7 = strong, 0.9 = near-certain
- **Domain-tagged**: enables filtered loading (e.g., only load `coding` instincts for coding tasks)
- **Evidence-backed**: tracks what observations created it
- **Scope-aware**: `global` applies everywhere; `project` is isolated

## Confidence Scoring (ECC-aligned)

| Score | Meaning | Behavior |
|-------|---------|----------|
| 0.3 | Tentative | Suggested but not enforced |
| 0.5 | Moderate | Applied when clearly relevant |
| 0.7 | Strong | Auto-applied in matching contexts |
| 0.9 | Near-certain | Core behavior, candidate for promotion |

### Confidence Changes
- New instinct starts at **0.5**
- Each independent confirmation: **+0.1** (cap at 1.0)
- Each contradiction (INSTINCT_CHALLENGE): **−0.1**
- No confirmation in 30 days: **−0.05/week** (decay)
- Below 0.3: **archive** to `instincts/archived/`
- Above 0.9: **promote** to company knowledge (copy to `docs/proven-patterns/`)

### Promotion Criteria (from ECC v2.1)
An instinct can be promoted to global company knowledge when:
- Confidence ≥ 0.9
- source_count ≥ 5
- Confirmed across ≥ 2 different task types or agents

## Scope Decision Guide (from ECC)

| Pattern Type | Scope | Examples |
|-------------|-------|---------|
| Framework conventions | **project** | "Use React hooks", "Follow Django patterns" |
| File structure | **project** | "Tests in `__tests__/`" |
| Code style | **project** | "Use functional style", "Prefer dataclasses" |
| Security practices | **global** | "Validate user input", "Sanitize SQL" |
| General best practices | **global** | "Write tests first", "Always handle errors" |
| Tool/workflow preferences | **global** | "Grep before Edit", "Read before Write" |
| Git practices | **global** | "Conventional commits", "Small focused PRs" |

## Feedback File Format

Agents append to `feedback/{date}.md` after each task:

```markdown
### {issue-id} — {agent-id} — {timestamp}

**Outcome**: success | partial | failure
**What went well**: (and WHY)
**What went wrong**: (and WHY)
**Missing info**: what would have helped
**Would do differently**: specific changes
**PATTERN_CANDIDATE**: {description} ← flag if you see a reusable pattern
**INSTINCT_CHALLENGE**: {instinct-name} ← flag if experience contradicts an instinct
```

## Metrics File Format

Agents write to `metrics/{agent-id}/{issue-id}.md`:

```yaml
---
issue: {issue-id}
agent: {agent-id}
date: {ISO date}
---
task_completion: 0-10
code_quality: 0-10
context_efficiency: 0-10
time_efficiency: 0-10
collaboration: 0-10
notes: "free-form observations"
```

## L0/L1/L2 Loading Protocol

To minimize token cost, agents use tiered loading:

- **L0** (always): Read `_index.md` — one-line per instinct, ~100 tokens total
- **L1** (on match): Read instinct frontmatter only — `id`, `trigger`, `confidence`, `domain`
- **L2** (on strong match): Read full instinct file — Pattern, Action, Evidence, Anti-pattern

**Rule**: Never load all instincts at L2. Start at L0, drill down only on matches.

## Loop 3: Skill Self-Creation Protocol

### When to Propose a Skill
An agent should create a skill proposal when:
1. A task required >3 steps of similar manual work that could be automated
2. A pattern appears in 2+ feedback entries as PATTERN_CANDIDATE
3. An INFRA_SIGNAL suggests a missing integration

### Proposal Format
Create `evolution/skill-drafts/SKILL-<name>.md`:

```markdown
---
proposed_by: <agent_name>
date: YYYY-MM-DD
source_tasks: [PET-xx, PET-yy]
category: tooling|workflow|integration
status: draft
---

# Skill: <name>

## Problem
What manual work or gap this addresses.

## Proposed Solution
What the skill would do.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Estimated Effort
Low / Medium / High
```

### Review Process
1. Agent creates draft in `evolution/skill-drafts/`
2. CTO reviews during biweekly skill review (or ad-hoc)
3. If approved → create actual skill via `skill-creator`
4. If rejected → move to `evolution/skill-drafts/rejected/` with reason

## Loop 4: SOUL.md Self-Modification Protocol

### When to Propose a SOUL Change
- After 3+ tasks reveal a behavioral pattern worth codifying
- When a monthly retrospective identifies a persistent communication or process gap
- When an agent discovers its current directives conflict with observed best practices

### Proposal Process
1. Agent writes `evolution/soul-proposals/SOUL-<topic>.md` with:
   - Current behavior description
   - Proposed change (diff format preferred)
   - Evidence from task feedback
   - Risk assessment
2. CTO reviews and adds technical assessment
3. Board vote (CEO + CTO consensus required)
4. If approved → update SOUL.md + commit with rationale
5. If rejected → archive with explanation

### Guardrails
- No agent can modify SOUL.md directly without Board approval
- Safety-critical clauses (Red Lines) require unanimous Board approval
- All changes tracked in git with linked proposal
