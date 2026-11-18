---
type: archive
status: closed
host: bkp-01
tickets: [CHG-4170, INC-20934]
created: 2026-10-14
---
# CHG-4170 · OS patching on bkp-01 (OpenSSH)

- **Window:** Friday 16 Oct 06:00 to 07:00 · risk low · RB-08
- **Result:** completed. Note of 21 Oct: the patching regenerated the SSH host keys, which broke WAL archiving from db-prd-02 ([[INC-20934 postgresql volume 93%]]).
