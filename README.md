# Embodied AI Platform

AI-powered development pipeline: **Paperclip** → **Linear** → **Symphony**

## Architecture

```
Paperclip (Discussion) → Linear (Tasks) → Symphony (Build)
   7 agents               Issues           Codex Agent
   Multi-model            States           Auto PR
```

## PET-7 CLI

`shorten.py` is a small URL shortener CLI that stores mappings in `urls.json`.

Examples:

```bash
python3 shorten.py https://example.com/very/long/path
python3 shorten.py --lookup 1e44d1
python3 shorten.py --list
```

Run tests with:

```bash
python3 -m pytest -q
```
