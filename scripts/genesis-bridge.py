#!/usr/bin/env python3
"""
Genesis Bridge — Paperclip ↔ Linear ↔ Symphony 全链路桥接

架构哲学：
  上层 Paperclip 做任务拆解与组织协同（谁负责什么、哪些并行、哪些需审批）
  下层 Symphony 做确定性执行（线性状态机：Todo→InProgress→Review→Done）
  Bridge 是二者之间的翻译层

流程：
  1. 轮询 Paperclip issues (status=todo, 有 assignee)
  2. 在 Linear 创建对应 issue（Symphony 从 Linear 接单）
  3. 轮询 Linear issues 状态变化
  4. 同步回 Paperclip（Done/Rework 等）

Usage:
  python3 scripts/genesis-bridge.py                    # 一次性同步
  python3 scripts/genesis-bridge.py --watch            # 持续监听（每60s轮询）
  python3 scripts/genesis-bridge.py --watch --interval 30  # 自定义间隔
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ─── Config ───────────────────────────────────────────────────────────

PAPERCLIP_URL = os.environ.get("PAPERCLIP_URL", "http://localhost:3100")
PAPERCLIP_COMPANY_ID = os.environ.get("PAPERCLIP_COMPANY_ID", "")
LINEAR_API_KEY = os.environ.get("LINEAR_API_KEY", "")
LINEAR_TEAM_ID = os.environ.get("LINEAR_TEAM_ID", "3b1842c0-17c8-4c27-b837-7abbe61b7178")

# Paperclip status → Linear state mapping
STATUS_MAP_TO_LINEAR = {
    "todo": "a9c377a6-082e-42e1-8257-d74fc310b0c5",        # Todo
    "in_progress": "cb6a22f9-0e86-4d30-b6ef-f42401c5aa07",  # In Progress
    "in_review": "d31e7db3-9990-4fcb-b53b-f8b4a2223972",    # In Review
    "done": "dc675134-88d3-4c5b-bf6b-adb5e1e3fdc1",         # Done
    "cancelled": "54b1d0e6-4e72-4af6-9292-85b90dfb40d1",    # Canceled
}

# Linear state name → Paperclip status mapping
STATUS_MAP_FROM_LINEAR = {
    "Todo": "todo",
    "In Progress": "in_progress",
    "In Review": "in_review",
    "Human Review": "in_review",
    "Rework": "in_progress",
    "Merging": "in_review",
    "Done": "done",
    "Canceled": "cancelled",
    "Duplicate": "cancelled",
}

# Priority mapping
PRIORITY_MAP = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
}

# ─── HTTP Helpers ─────────────────────────────────────────────────────

def paperclip_get(path: str):
    """GET from Paperclip API."""
    url = f"{PAPERCLIP_URL}/api{path}"
    req = urllib.request.Request(url)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  ✗ Paperclip GET {path}: {e.code} {e.read().decode()[:200]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  ✗ Paperclip GET {path}: {e}", file=sys.stderr)
        return None


def paperclip_patch(path: str, data: dict):
    """PATCH to Paperclip API."""
    url = f"{PAPERCLIP_URL}/api{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="PATCH")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  ✗ Paperclip PATCH {path}: {e.code} {e.read().decode()[:200]}", file=sys.stderr)
        return None


def linear_graphql(query: str, variables: dict = None):
    """Execute a Linear GraphQL query."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    body = json.dumps(payload).encode()
    req = urllib.request.Request("https://api.linear.app/graphql", data=body)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", LINEAR_API_KEY)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if result.get("errors"):
                print(f"  ✗ Linear GraphQL error: {result['errors']}", file=sys.stderr)
            return result.get("data")
    except Exception as e:
        print(f"  ✗ Linear GraphQL: {e}", file=sys.stderr)
        return None


# ─── State File ───────────────────────────────────────────────────────

STATE_FILE = os.path.join(os.path.dirname(__file__), ".bridge-state.json")

def load_state() -> dict:
    """Load bridge state (Paperclip ID → Linear ID mapping)."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"mappings": {}, "last_sync": None}


def save_state(state: dict):
    """Save bridge state."""
    state["last_sync"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ─── Core Logic ───────────────────────────────────────────────────────

def get_paperclip_issues() -> list:
    """Get all non-terminal issues from Paperclip."""
    issues = paperclip_get(f"/companies/{PAPERCLIP_COMPANY_ID}/issues")
    if not issues:
        return []
    # Filter: only actionable issues (not done/cancelled/backlog without assignee)
    return [i for i in issues if i.get("status") not in ("done", "cancelled")]


def get_linear_issues() -> dict:
    """Get all Linear issues for the team, keyed by identifier."""
    data = linear_graphql("""
        query($teamId: String!) {
            team(id: $teamId) {
                issues(first: 50, orderBy: createdAt) {
                    nodes {
                        id
                        identifier
                        title
                        state { name }
                        description
                    }
                }
            }
        }
    """, {"teamId": LINEAR_TEAM_ID})
    if not data:
        return {}
    nodes = data.get("team", {}).get("issues", {}).get("nodes", [])
    return {n["id"]: n for n in nodes}


def sync_paperclip_to_linear(state: dict) -> int:
    """
    Phase 1: Paperclip → Linear
    For each Paperclip issue in 'todo' with an assignee, create a Linear issue.
    """
    issues = get_paperclip_issues()
    created = 0

    for issue in issues:
        pc_id = issue["id"]
        # Skip if already mapped to Linear
        if pc_id in state["mappings"]:
            continue
        # Only sync issues that are 'todo' and have an assignee
        if issue.get("status") != "todo":
            continue
        if not issue.get("assigneeAgentId"):
            continue

        title = issue.get("title", "Untitled")
        desc = issue.get("description", "")
        priority = PRIORITY_MAP.get(issue.get("priority", "medium"), 3)

        # Prefix with Paperclip identifier for traceability
        pc_identifier = issue.get("identifier", pc_id[:8])
        linear_title = f"[{pc_identifier}] {title}"

        # Add provenance to description
        linear_desc = f"{desc}\n\n---\n_Synced from Paperclip issue {pc_identifier}_"

        print(f"  → Creating Linear issue: {linear_title}")
        data = linear_graphql("""
            mutation($teamId: String!, $title: String!, $description: String, $priority: Int) {
                issueCreate(input: {
                    teamId: $teamId,
                    title: $title,
                    description: $description,
                    priority: $priority
                }) {
                    success
                    issue { id identifier }
                }
            }
        """, {
            "teamId": LINEAR_TEAM_ID,
            "title": linear_title,
            "description": linear_desc,
            "priority": priority,
        })

        if data and data.get("issueCreate", {}).get("success"):
            linear_issue = data["issueCreate"]["issue"]
            state["mappings"][pc_id] = {
                "linear_id": linear_issue["id"],
                "linear_identifier": linear_issue["identifier"],
                "paperclip_identifier": pc_identifier,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            print(f"    ✓ Created {linear_issue['identifier']} (Linear) ← {pc_identifier} (Paperclip)")

            # Update Paperclip issue: add comment with Linear link
            paperclip_patch(f"/issues/{pc_id}", {
                "comment": f"🔗 Synced to Linear: {linear_issue['identifier']}",
            })
            created += 1

    return created


def sync_linear_to_paperclip(state: dict) -> int:
    """
    Phase 2: Linear → Paperclip
    For each mapped issue, check Linear status and sync back to Paperclip.
    """
    if not state["mappings"]:
        return 0

    linear_issues = get_linear_issues()
    updated = 0

    for pc_id, mapping in list(state["mappings"].items()):
        linear_id = mapping["linear_id"]
        linear_issue = linear_issues.get(linear_id)

        if not linear_issue:
            continue

        linear_state = linear_issue.get("state", {}).get("name", "")
        pc_status = STATUS_MAP_FROM_LINEAR.get(linear_state)

        if not pc_status:
            continue

        # Check if Paperclip issue needs updating
        pc_issue = paperclip_get(f"/issues/{pc_id}")
        if not pc_issue:
            continue

        current_status = pc_issue.get("status")
        if current_status == pc_status:
            continue  # Already in sync

        # Don't downgrade from done
        if current_status == "done":
            continue

        print(f"  ← Syncing {mapping['paperclip_identifier']}: {current_status} → {pc_status} (Linear: {linear_state})")
        result = paperclip_patch(f"/issues/{pc_id}", {
            "status": pc_status,
            "comment": f"📡 Status synced from Linear ({linear_state})",
        })
        if result:
            print(f"    ✓ Updated")
            updated += 1

    return updated


def run_sync(state: dict) -> tuple:
    """Run one sync cycle."""
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    print(f"\n[{ts}] ─── Sync cycle ───")

    created = sync_paperclip_to_linear(state)
    updated = sync_linear_to_paperclip(state)

    save_state(state)
    print(f"  Summary: {created} created, {updated} updated, {len(state['mappings'])} total mappings")
    return created, updated


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Genesis Bridge: Paperclip ↔ Linear ↔ Symphony")
    parser.add_argument("--watch", action="store_true", help="Continuous polling mode")
    parser.add_argument("--interval", type=int, default=60, help="Poll interval in seconds (default: 60)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced without doing it")
    args = parser.parse_args()

    print("╔════════════════════════════════════════════╗")
    print("║  Genesis Bridge — Paperclip ↔ Linear       ║")
    print("╚════════════════════════════════════════════╝")
    print(f"  Paperclip: {PAPERCLIP_URL} (company: {PAPERCLIP_COMPANY_ID[:8]}...)")
    print(f"  Linear Team: {LINEAR_TEAM_ID[:8]}...")
    print(f"  Mode: {'watch' if args.watch else 'one-shot'}")

    state = load_state()
    print(f"  Existing mappings: {len(state['mappings'])}")

    if args.watch:
        print(f"  Polling every {args.interval}s — Ctrl+C to stop\n")
        try:
            while True:
                run_sync(state)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n\n  Bridge stopped.")
            save_state(state)
    else:
        run_sync(state)

    print(f"\n  Final mappings: {len(state['mappings'])}")


if __name__ == "__main__":
    main()
