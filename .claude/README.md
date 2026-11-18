# Workshop 4 · Part 3 with Claude Code (back-up)

For participants with a Claude seat. Same slides, same WS4 files, same hands-on. Only the harness changes: Claude Code instead of OpenCode.

**Privacy.** Claude Code sends your prompts and the files it reads to Anthropic, under your company's Claude agreement. The WS4 data is fictitious. Use this only with the WS4 training data, unless your company's policy says otherwise.

## Where the files are, and why

| File | What it is | Why there |
|---|---|---|
| `.claude/agents/ops.md` | The ops agent from Part 2 | Claude Code finds agents, skills and commands by walking up from the folder where it starts |
| `.claude/agents/log-reader.md` | Hands-on E, with the two WRITE ME | (same) |
| `.claude/skills/` | disk-alert-triage and plan-my-day, adapted to Claude Code's tools | (same) |
| `.claude/commands/handover.md` | Hands-on G, with the three WRITE ME | (same) |
| `.claude/hooks/guard.mjs` | Hands-on B: the guard, `PROTECTED = ["WRITE ME"]` | Any path; settings.json points to it |
| `.claude/solutions/` | The three files filled in | Copy one over if you are short of time |
| `WS4/.claude/settings.json` | Starts the session as ops; asks before shell, edits and vault writes; runs the guard | Claude Code reads settings.json only from the folder where it starts |
| `WS4/.mcp.json` | The runbooks (read-only) and vault servers | The folder where Claude Code starts |

Always start Claude Code **in WS4**: `cd WS4` then `claude`. Do not add a `CLAUDE.md`: Claude Code reads `AGENTS.md` only when there is no `CLAUDE.md`.

## Slide by slide

**Slide 5 · Restart check.**
1. In WS4: `git pull`, then `cp solutions/AGENTS.md AGENTS.md`.
2. Start: `claude`.
3. The first time, approve the two project servers, runbooks and vault. The vault fails to connect until slide 68 creates its folder; that is expected.
4. Ask `Run df -h`. It must ask first. Answer no.

**Slide 11 · Hands-on A.** Same steps and prompt. Answer no to every ask.

**Slide 19 · Hands-on B.**
1. In `../.claude/hooks/guard.mjs` (from WS4), set `PROTECTED = ["pg_wal"]`. No restart: the hook reads the file at every call.
2. Run test 1 and test 2 from the slide.
3. Expected: test 1 is blocked with no ask, because the hook runs before the permission rules; test 2 asks.

**Slide 20 · Fail open or closed?** A Claude Code hook that crashes lets the call through by default. Ours sets `"onFailure": "block"` in settings.json, so it fails closed. Compare with OpenCode, which failed open in the trainer's test.

**Slide 33 · Hands-on C.**
1. Start Jaeger as on the slide.
2. Claude Code ignores telemetry variables in a project's settings, so set them in the terminal, before `claude` (PowerShell: `$env:NAME="value"`):
   ```bash
   export CLAUDE_CODE_ENABLE_TELEMETRY=1
   export CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1
   export OTEL_TRACES_EXPORTER=otlp
   export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
   export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
   ```
3. Run the two runs, then open Jaeger. Pick the Claude Code service.
4. The spans:
   - `claude_code.interaction`: one per prompt;
   - `claude_code.llm_request`;
   - `claude_code.tool`, with `claude_code.tool.blocked_on_user` (your wait) and `claude_code.tool.execution`.
5. Question 3: who blocked what is a log event (`claude_code.tool_decision`, source `hook`), not a span. Jaeger shows traces only.

**Slide 42 · Hands-on D.** The loop, with `claude -p`. In `-p` mode a call that needs approval is denied, so allow file writes and cap the turns:
```bash
for i in 1 2 3; do
  claude -p "We got a disk alert on db-prd-02. Triage it." \
    --permission-mode acceptEdits --max-turns 15 > runs/run$i.md
done
```

**Slides 56–57 · Hands-on E.**
1. Fill the two WRITE ME in `../.claude/agents/log-reader.md`, then restart `claude`.
2. Use the same prompt. To force the worker, type `@`, then pick log-reader.
3. Done when you see two `Agent` calls, one per host, each returning the block.
4. Workers cannot start their own workers: their only tool is `Read`.

**Slide 59 · Hands-on F.** Same as the slide, in `../.claude/agents/log-reader.md`.

**Slide 68 · The vault.** Same commands. Then type `/mcp` in Claude Code and reconnect **vault**.

**Slides 70–71 · Hands-on G.**
1. Fill the three WRITE ME in `../.claude/commands/handover.md`.
2. Type `/handover`. Read each vault write before you approve it.
3. Who keeps the archive read-only: the guard. In Claude Code a hook sees the MCP tool's path, and `guard.mjs` blocks any write into `4_Archive`. A settings.json rule cannot match an MCP tool's argument: Claude Code skips any `mcp__` rule that has parentheses.

**Slide 72 · The schedule line.**
```bash
claude -p "/handover" --allowedTools "mcp__vault__write_file,mcp__vault__edit_file,mcp__vault__create_directory" --max-turns 30 >> runs/0315.log 2>&1
```
`-p` denies anything not allowed. The guard still holds.

## Windows

- **Hooks:** they run in Git Bash, or in PowerShell when Git Bash is not installed. The hook line in settings.json is written for Git Bash: install Git for Windows.
- **Servers:** if runbooks or vault do not start, replace `"command": "npx"` in `WS4/.mcp.json` with `"command": "cmd"`, and put `"/c", "npx",` at the start of `args`.

Written for Claude Code 2.1.327 (18 Nov 2026).
