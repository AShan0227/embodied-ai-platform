#!/usr/bin/env python3
"""
Genesis Calendar Checker — macOS Calendar integration

Uses icalBuddy (if installed) or AppleScript to check upcoming events.

Usage:
  python3 scripts/check-calendar.py              # Next 24h events
  python3 scripts/check-calendar.py --hours 48   # Next 48h events
"""

import argparse
import subprocess
import sys
from datetime import datetime

def check_icalbuddy(hours=24):
    """Use icalBuddy if available."""
    try:
        result = subprocess.run(
            ["icalBuddy", "-n", "-ea", f"eventsFrom:today to:today+{hours//24}d"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None

def check_applescript(hours=24):
    """Fallback: use AppleScript to query Calendar.app."""
    script = f'''
    tell application "Calendar"
        set now to current date
        set endDate to now + ({hours} * 60 * 60)
        set eventList to {{}}
        repeat with cal in calendars
            set evts to (every event of cal whose start date >= now and start date <= endDate)
            repeat with evt in evts
                set end of eventList to (summary of evt) & " | " & (start date of evt as string)
            end repeat
        end repeat
        return eventList as string
    end tell
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None

def main():
    parser = argparse.ArgumentParser(description="Genesis Calendar Checker")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look ahead (default: 24)")
    args = parser.parse_args()
    
    # Try icalBuddy first, then AppleScript
    events = check_icalbuddy(args.hours) or check_applescript(args.hours)
    
    if not events:
        print(f"📅 No events in the next {args.hours}h (or Calendar access not configured)")
        return
    
    print(f"📅 Upcoming events (next {args.hours}h):\n")
    for line in events.split(", "):
        if "|" in line:
            name, time = line.split("|", 1)
            print(f"  • {name.strip()} — {time.strip()}")
        elif line.strip():
            print(f"  • {line.strip()}")

if __name__ == "__main__":
    main()
