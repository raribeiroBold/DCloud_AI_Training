# WS4 · guide for agents

The K+N operations training folder: the logs and runbooks of our hosts, and the files the agents write. Every agent that works in this folder reads this guide.

## Where things are
- logs/: one file per host, logs/<host>.log (for example logs/db-prd-02.log).
- runbooks/: RB-01.html to RB-10.html, one procedure each.
- tickets/: draft tickets. The create_ticket tool writes them here.
- notes/: notes the agents keep between sessions. Not in Git.
- data/day/: one working day, Wednesday 21 October 2026, exported from Outlook: calendar.ics and inbox/ (one .eml file per mail).

## How to work here
- For a question about a host, read notes/handoff.md first if it exists, then logs/<host>.log to check it. Do not search for the words of the question.
- To open a file, use read. To list the files in a folder, use glob (for example data/day/inbox/*.eml).
- For runbooks, use the runbooks tools (runbooks_search_files, runbooks_read_text_file) when that server is connected; they reach only runbooks/. When it is off, open runbooks/ with read.
- Write only in tickets/ and notes/. Never change logs/, runbooks/ or data/.

## Notes between sessions
- At the start, read notes/handoff.md if it exists. At the end, update it: current task, done, next, decisions, with a date and a source on each line.
- Write only what you checked in a file.

## Never
- Never write tokens, passwords or personal data in any file.
