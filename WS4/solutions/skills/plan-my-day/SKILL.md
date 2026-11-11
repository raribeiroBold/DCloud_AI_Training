---
name: plan-my-day
description: "Plan the work day from today's calendar, the inbox and the open alerts, and propose the three priorities and time blocks. Use when someone asks to plan the day, what to do first, or for a morning briefing. Not for replying to mail or for scheduling meetings."
---
# Plan my day

## Steps
1. Read today's calendar: data/day/calendar.ics. List every meeting with its start and end time.
2. Read every mail in data/day/inbox/, one file at a time, all of them. For each mail: who, what they ask, and by when.
3. Read notes/handoff.md if it exists. For a CRITICAL alert mail, read the host's log in logs/<host>.log.
4. Pick the three priorities for today, most urgent first, each with its source (the mail, the meeting or the log line).
5. Fit the priorities into the free time between meetings. Show any two meetings that overlap.
6. Write the plan to notes/day-plan.md with the write tool.

## Rules
- May do alone: read data/day/, logs/, tickets/ and notes/, with read and glob (the runbooks tools reach only runbooks/).
- Must ask first: writing notes/day-plan.md.
- Never: send, reply to or forward a mail; accept, decline or move a meeting; approve or reject a change.

## Gotchas
- A CRITICAL alert beats any meeting. Check it in the host's log, not only in the alert mail.
- An approval asked for "before" a meeting is due when that meeting starts, not at the end of the day.
- Newsletters and sales offers go to "Can wait"; do not plan time for them.

## Output
In notes/day-plan.md, the full plan:
1. Top three priorities, each with its source
2. The day in time blocks, meetings fixed
3. Conflicts
4. Can wait, with one reason each
5. What you did not do (nothing was sent)

In your answer, once the file is written, five lines or less: the three priorities, any conflict, and where the full plan is.
