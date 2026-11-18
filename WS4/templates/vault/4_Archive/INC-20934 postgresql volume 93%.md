---
type: archive
status: closed
host: db-prd-02
tickets: [INC-20934, CHG-4170]
created: 2026-10-21
---
# INC-20934 · db-prd-02 /var/lib/postgresql at 93%

- **When:** 21 Oct 03:20 to 11:09 · P2 · RB-02
- **Cause:** [[CHG-4170 bkp-01 patching]] generated new SSH host keys on bkp-01 on 16 Oct; the archive command (rsync over ssh) failed host key verification.
- **Fix:** the new bkp-01 host key added to known_hosts of the postgres user on db-prd-02 (RB-02 step 2); archiving caught up.
