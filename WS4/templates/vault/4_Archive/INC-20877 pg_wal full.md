---
type: archive
status: closed
host: db-prd-02
tickets: [INC-20877]
created: 2026-10-06
---
# INC-20877 · PostgreSQL PANIC on db-prd-02: pg_wal full

- **When:** 6 Oct 23:31 to 7 Oct 16:02 · P1 · RB-02
- **Cause:** `/srv/wal` on bkp-01 was not mounted after the reboot of 4 Oct. Every archive attempt failed from 5 Oct 01:02 (rsync: Permission denied), and pg_wal grew until /var/lib/postgresql was full.
- **Fix:** `/srv/wal` mounted on bkp-01, fstab entry corrected, PostgreSQL restarted; archiving caught up overnight.
- **Lesson:** the 95% alert at 03:12 on 6 Oct was not acted on.
