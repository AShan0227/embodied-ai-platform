# Evolution System

The company's learning backbone. Four loops, four speeds.

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

## Instinct File Format

Borrowed from ECC's continuous learning model. Each instinct file uses this frontmatter:

```yaml
---
confidence: 0.7          # 0.0–1.0, increases with confirmations
source_count: 3           # independent observations supporting this
created: 2026-03-15
last_confirmed: 2026-03-15
category: coding|architecture|process|communication
---
# Instinct: {name}

## Pattern
What triggers this instinct — the situation to recognize.

## Action
What to do when this pattern is detected.

## Evidence
Summarized examples from feedback entries.

## Anti-pattern
What NOT to do (learned from failures).
```

## Confidence Rules

- New instinct starts at 0.5
- Each independent confirmation: +0.1 (cap at 1.0)
- Each contradiction (INSTINCT_CHALLENGE): −0.1
- No confirmation in 30 days: −0.05/week (decay)
- Below 0.3: archive to `instincts/archived/`
- Above 0.9: promote to company knowledge (copy to `docs/proven-patterns/`)

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
