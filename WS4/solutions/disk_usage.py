# Disk usage per mount for one host, read from logs/<host>.log.
# Deterministic: the same log gives the same answer every time.
# Errors are printed as short text, so the model can read them.
import re
import sys

host = sys.argv[1] if len(sys.argv) > 1 else ""
if not re.fullmatch(r"[a-z0-9.-]+", host):
    print("Error: host must look like db-prd-02.")
    sys.exit(0)

last = {}
try:
    with open(f"logs/{host}.log") as log:
        for line in log:
            m = re.search(r"diskmon\[\d+\]: (\S+) used=(\d+)% \(([^)]*)\)", line)
            if m:
                mount, pct, size = m.groups()
                last[mount] = f"{mount} {pct}% ({size}), {line[:15]}"
except FileNotFoundError:
    print(f"Error: no log for {host}.")
    sys.exit(0)

print("\n".join(last.values()) if last else f"No disk lines for {host}.")
