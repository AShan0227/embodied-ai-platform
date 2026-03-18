# Embodied AI Platform

AI-powered development pipeline: **Paperclip** → **Linear** → **Symphony**

## Current Deliverables

- Strategic research report for `PET-8`: [strategic-research-task.md](strategic-research-task.md)
- Tracker handoff payloads for `PET-8`: [docs/PET-8-linear-handoff.md](docs/PET-8-linear-handoff.md)

## Architecture

```
Paperclip (Discussion) → Linear (Tasks) → Symphony (Build)
   7 agents               Issues           Codex Agent
   Multi-model            States           Auto PR
```

## Deliverables

- `scripts/fibonacci.py`: Python CLI for printing the first N Fibonacci numbers, with input validation and optional JSON output.
- `scripts/test_fibonacci.py`: Pytest coverage for normal cases, edge cases, and `--json` output.
