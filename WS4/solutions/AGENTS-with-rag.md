# WS4 · guide for agents

The K+N operations training folder: the logs and runbooks of our hosts, and the files the agents write. Every agent that works in this folder reads this guide.

## Where things are
- logs/: one file per host, logs/<host>.log (for example logs/db-prd-02.log).
- runbooks/: RB-01.html to RB-10.html, one procedure each, also indexed in the runbooks collection of the rag server.
- tickets/: draft tickets. The create_ticket tool writes them here.
- notes/: notes the agents keep between sessions. Not in Git.
- data/day/: one working day, Wednesday 21 October 2026, exported from Outlook: calendar.ics and inbox/ (one .eml file per mail).

## How to work here
- For a question about a host, read logs/<host>.log first. Do not search for the words of the question.
- To open a file, use read. To list the files in a folder, use glob (for example data/day/inbox/*.eml).
- For any runbook question, call rag_chroma_query_documents on the runbooks collection first, with the question as the query. Do not search or list the runbooks/ folder.
- Write only in tickets/ and notes/. Never change logs/, runbooks/ or data/.

## Never
- Never write tokens, passwords or personal data in any file.
