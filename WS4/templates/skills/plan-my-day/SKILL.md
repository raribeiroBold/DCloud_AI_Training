---
name: plan-my-day
description: "[WHAT it does, in one sentence]. Use when [WHEN: the words someone uses to ask for it]. Not for [WHEN NOT: the closest task it must not do]."
---
# Plan my day

<!-- Step by step: fill each [ ] as the slide says, then delete this comment.
     Keep the description inside its double quotes, and use no other double quotes in it.
     Restart OpenCode after saving. -->

## Steps
1. Read today's calendar: [FILE: the .ics file in data/day/]. List every meeting with its start and end time.
2. Read every mail in [FOLDER: the inbox folder in data/day/], one file at a time, all of them. For each mail: who, what they ask, and by when.
3. Read notes/handoff.md if it exists. For a CRITICAL alert mail, read the host's log in logs/<host>.log.
4. Pick the three priorities for today, most urgent first, each with its source (the mail, the meeting or the log line).
5. Fit the priorities into the free time between meetings. Show any two meetings that overlap.
6. Write the plan to notes/day-plan.md with the write tool.

## Rules
- May do alone: read data/day/, logs/, tickets/ and notes/, with read and glob (the runbooks tools reach only runbooks/).
- Must ask first: [WHAT CHANGES SOMETHING]
- Never: send, reply to or forward a mail; accept, decline or move a meeting; [ONE MORE NEVER]

## Gotchas
- A CRITICAL alert beats any meeting. Check it in the host's log, not only in the alert mail.
- [YOUR GOTCHA: what a new colleague gets wrong when planning a day here]

## Output
In notes/day-plan.md, the full plan:
1. Top three priorities, each with its source
2. The day in time blocks, meetings fixed
3. Conflicts
4. Can wait, with one reason each
5. What you did not do (nothing was sent)

In your answer, once the file is written, five lines or less: the three priorities, any conflict, and where the full plan is.
