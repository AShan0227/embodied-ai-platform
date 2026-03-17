# Embodied AI Platform

AI-powered development pipeline: **Paperclip** → **Linear** → **Symphony**

## Architecture

```
Paperclip (Discussion) → Linear (Tasks) → Symphony (Build)
   7 agents               Issues           Codex Agent
   Multi-model            States           Auto PR
```

## Deliverables

- `scripts/fibonacci.py`: Python CLI for printing the first N Fibonacci numbers, with input validation and optional JSON output.
- `scripts/test_fibonacci.py`: Pytest coverage for normal cases, edge cases, and `--json` output.
