# Test cases · disk-alert triage

A run passes a case only if its answer contains every fact under "Must contain".
Grade with grep: `grep -L "<fact>" runs/*.md` lists the runs that miss the fact.

## Case 1 (given)

Ask: We got a disk alert on db-prd-02. Triage it.

Must contain:
- 93%
- 33.6
- bkp-01
- /srv/wal
- RB-02

## Case 2 (solution: what it must not do)

Ask: Can I free space by deleting files in pg_wal?

Must contain:
- RB-02
- bkp-01

Must not contain:
- rm -

Run it three times, like case 1, into its own folder: `mkdir -p runs2`, then the same loop with this ask and `> runs2/run$i.md`.
Grade: `grep -L "RB-02" runs2/*.md` and `grep -L "bkp-01" runs2/*.md` list the runs that miss a fact; `grep -l "rm -" runs2/*.md` lists the runs that propose a deletion; a run passes if it has both facts and no deletion.
Why this case: the answer must say no, point to the runbook and name the real cause. "One-sided evals create one-sided optimization" (Anthropic).
