---
description: "Write the shift handover into the vault at the end of a shift with an open incident. Never changes a host."
---
Write the shift handover for tonight's WAL incident on db-prd-02.

Read first:
- notes/handoff.md
- the newest ticket draft in tickets/
- the log lines you cite, from logs/

Write with the vault tools only (mcp__vault__…):
1. ../ops-vault/1_Projects/2026-11-19 WAL archiving db-prd-02/Handover 2026-11-19.md,
   from ../ops-vault/98_Templates/Handover.md. Fill every section.
2. Update the "Current state" section of ../ops-vault/2_Areas/db-prd-02/db-prd-02.md.
   If the note does not exist, create it from ../ops-vault/98_Templates/Area.md
   with the facts from data/cmdb.csv.

Never: write in 4_Archive, 3_Resources or 98_Templates.

End your answer with one list: what you could not check.
