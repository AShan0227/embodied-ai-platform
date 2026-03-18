#!/usr/bin/env python3
"""
Genesis Inbox Checker — IMAP email monitoring

Checks for unread emails and returns a summary.
Configure via environment variables:
  IMAP_HOST, IMAP_USER, IMAP_PASSWORD, IMAP_FOLDER (default: INBOX)

Usage:
  python3 scripts/check-inbox.py              # Check unread count
  python3 scripts/check-inbox.py --summary    # Show subject lines
  python3 scripts/check-inbox.py --since 24h  # Only last 24 hours
"""

import argparse
import imaplib
import email
import os
import sys
from datetime import datetime, timedelta
from email.header import decode_header

IMAP_HOST = os.environ.get("IMAP_HOST", "")
IMAP_USER = os.environ.get("IMAP_USER", "")
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD", "")
IMAP_FOLDER = os.environ.get("IMAP_FOLDER", "INBOX")

def connect():
    if not all([IMAP_HOST, IMAP_USER, IMAP_PASSWORD]):
        print("⚠️  Email not configured. Set IMAP_HOST, IMAP_USER, IMAP_PASSWORD env vars.")
        sys.exit(0)
    mail = imaplib.IMAP4_SSL(IMAP_HOST)
    mail.login(IMAP_USER, IMAP_PASSWORD)
    mail.select(IMAP_FOLDER)
    return mail

def decode_subject(msg):
    subject = msg.get("Subject", "")
    decoded = decode_header(subject)
    parts = []
    for content, charset in decoded:
        if isinstance(content, bytes):
            parts.append(content.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(content)
    return " ".join(parts)

def check_unread(since_hours=None):
    mail = connect()
    
    if since_hours:
        since_date = (datetime.now() - timedelta(hours=since_hours)).strftime("%d-%b-%Y")
        _, data = mail.search(None, f'(UNSEEN SINCE {since_date})')
    else:
        _, data = mail.search(None, "UNSEEN")
    
    ids = data[0].split()
    return mail, ids

def main():
    parser = argparse.ArgumentParser(description="Genesis Inbox Checker")
    parser.add_argument("--summary", action="store_true", help="Show subject lines")
    parser.add_argument("--since", type=str, help="Time window (e.g., 24h, 48h)")
    args = parser.parse_args()
    
    since_hours = None
    if args.since:
        since_hours = int(args.since.rstrip("h"))
    
    mail, ids = check_unread(since_hours)
    count = len(ids)
    
    if not args.summary:
        print(f"📬 {count} unread email{'s' if count != 1 else ''}")
        mail.logout()
        return
    
    print(f"📬 {count} unread email{'s' if count != 1 else ''}:\n")
    for i, eid in enumerate(ids[-10:], 1):  # Last 10
        _, msg_data = mail.fetch(eid, "(BODY.PEEK[HEADER])")
        msg = email.message_from_bytes(msg_data[0][1])
        subject = decode_subject(msg)
        sender = msg.get("From", "unknown")
        date = msg.get("Date", "")
        print(f"  {i}. {subject}")
        print(f"     From: {sender}")
        print(f"     Date: {date}\n")
    
    if count > 10:
        print(f"  ... and {count - 10} more")
    
    mail.logout()

if __name__ == "__main__":
    main()
