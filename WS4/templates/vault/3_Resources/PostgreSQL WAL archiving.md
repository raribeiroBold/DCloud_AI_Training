---
type: resource
status: active
host: db-prd-02
tickets: []
created: 2026-11-19
---
# PostgreSQL WAL archiving

- db-prd-02 archives every WAL file to bkp-01 (`/srv/wal`) with rsync over ssh.
- When archiving fails, PostgreSQL keeps the WAL files in `pg_wal`, and the volume fills.
- Runbook: RB-02 (`runbooks/RB-02.html`).
- Gotcha: never clean `pg_wal` by hand. Fix the archiving, then let it catch up.
- Seen before: [[INC-20877 pg_wal full]] (mount missing), [[INC-20934 postgresql volume 93%]] (SSH host key), [[CHG-4170 bkp-01 patching]].
