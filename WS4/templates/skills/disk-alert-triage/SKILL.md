---
name: disk-alert-triage
description: Triage a disk-space alert on a Linux host from its log in logs/ - usage per mount, the trend, the likely cause, the matching runbook and a draft ticket. Use when someone reports a disk, volume or filesystem alert on a host. Not for capacity planning, and not for freeing space.
---
# Disk alert triage

## Steps
1. Read notes/handoff.md if it exists. Then read logs/<host>.log. Find the last disk-usage line for each mount, and the earlier reading for the same mount.
2. Work out the hours until full with the calculator, one step at a time: the hours between the two readings (from their timestamps), the growth per hour, then the free space divided by the growth per hour. Do not compute anything yourself.
3. In the same log, look for errors near the alert that explain the growth (for example failed WAL archiving).
4. Find the matching runbook with the runbooks tools.
5. Draft a ticket with the create_ticket tool.

## Rules
- Read only. Never delete, move or compress files, and never restart a service.
- Cite the log line or runbook section for every claim.

## Gotchas
- A full pg_wal is a symptom: WAL archiving is failing. Never clean pg_wal by hand (RB-02).
- Give the percentage and the free space: 93% of 500G is still 35G free.
- Two readings at the same time on two consecutive days are 24 hours apart.

## Output
1. Host and mount: usage now and before, with the log lines
2. Hours until full (from the calculator)
3. Likely cause, with the log line
4. Runbook and the draft ticket
