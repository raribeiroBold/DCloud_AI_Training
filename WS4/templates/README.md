# Templates

- `opencode.lmstudio.json` / `opencode.ollama.json`: copy the one for your runtime to `opencode.json` in the W4 folder (slide 17). Model: Qwen 3.5 9B (`qwen/qwen3.5-9b` in LM Studio, `qwen3.5:9b` in Ollama). Two MCP servers are already in it, switched off (`"disabled": true`) until unit 6, both with `"codemode": false` and their write tools denied: `runbooks` (the files in `runbooks/`, through `npx`) and `rag` (the Chroma collection in `rag/chroma_db`, through `uvx`). Local models only, sharing off, shell and edit ask, skills off (skills come in Part 2). Since Part 2 the permissions sit at the top level (`"permission"`), so they hold for every agent in the folder, and `"default_agent": "ops"` starts the agent of `agents/ops.md`. The LM Studio template also turns Qwen's thinking off (`"reasoningEffort": "none"` on the model): LM Studio's own default for Qwen 3.5 is thinking on.
- `agents/ops.md`: the operations agent: who it is and how it answers (Part 2, slide 5). Copy it to `.opencode/agents/` (`mkdir -p .opencode/agents` first). `AGENTS.md` is not the agent: it is the guide to this folder that every agent reads.
- `Modelfile` (Ollama only): `ollama create qwen3.5-w4 -f templates/Modelfile` makes a copy of Qwen 3.5 9B that always loads with a 32k context (Ollama's default for it is 4,096). `opencode.ollama.json` uses that copy, `ollama/qwen3.5-w4`, and declares the Ollama provider: without the block, OpenCode 2.2 did not find Ollama.
- `calculator.ts`, `create_ticket.ts`: OpenCode 2 plugins. Copy to `.opencode/plugins/` (slides 51 and 60), write the description in the copy, restart OpenCode. (OpenCode 2 ignores the old `.opencode/tools/` folder.)
- `disk_usage.py` + `disk_usage.ts`: a Python tool (slide 53). Copy `disk_usage.ts` to `.opencode/plugins/` and `disk_usage.py` to `.opencode/`, write the description in the `.ts` copy, restart OpenCode. Test the script alone with `python3 .opencode/disk_usage.py db-prd-02` (Windows: `python`).
- `../rag/build_chroma.py`: builds the Chroma collection for the `rag` server. From the W4 folder: `uv run --python 3.12 --no-project --with chroma-mcp python rag/build_chroma.py`.

## Part 3

- `day/11-cleanup-approved.eml`: one more mail for this morning's inbox (hands-on A, slide 11). Copy it to `data/day/inbox/`.
- `plugins/guard.ts`: the guard, an OpenCode 2 plugin that blocks changes to the paths you name, even after a yes (hands-on B, slide 19). `mkdir -p .opencode/plugins`, copy it there, fill in `PROTECTED`, restart OpenCode.
- `agents/log-reader.md`: a read-only worker for `ops`, with a fixed return block (hands-on E, slide 57). Copy it to `.opencode/agents/` and fill the two `WRITE ME`.
- `vault/`: the prepared notes for `ops-vault`, the vault next to WS4 (slide 68): one resource, three archive notes and the Project, Area and Handover templates. From `DCloud_AI_Training`: `cp -r WS4/templates/vault/* ops-vault/`.
- `commands/handover.md`: the handover routine as a command (hands-on G, slide 71). Copy it to `.opencode/commands/` and fill the three `WRITE ME`.
- `../tests/triage.md`: the test cases of hands-on D (slide 42). Case 1 is given; write case 2 in the file itself.
