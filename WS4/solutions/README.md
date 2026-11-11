# Solutions

The working versions, tested on the trainer's laptop with Qwen 3.5 9B in LM Studio. Use them if you are stuck; copy, do not edit them here.

- `AGENTS.md`: the guide to this folder that every agent reads (where things are, how to work here, what never to do). Rewritten for Part 2: in Part 1 it also held the agent's role, which now lives in `templates/agents/ops.md`.
- `AGENTS-with-mcp.md`: adds the line that sends runbook questions to the runbooks MCP server (Part 2, slide 19).
- `AGENTS-with-rag.md`: sends runbook questions to the RAG server instead.
- `AGENTS-with-memory.md`: adds the handoff notes in `notes/handoff.md` (Part 2, slide 56).
- `opencode.json`: the full settings at the end of the session, for LM Studio: both MCP servers on (`runbooks` and `rag`), write tools denied. Copy it to the W4 folder, then quit and start OpenCode with `--standalone`.
- `opencode.ollama.json`: the same for Ollama. Copy it to the W4 folder as `opencode.json`.
- `plugins/calculator.ts`, `plugins/create_ticket.ts`, `plugins/disk_usage.ts`: the three tools with their descriptions written. Copy them to `.opencode/plugins/`; `disk_usage.ts` also needs `disk_usage.py` in `.opencode/`.
- `disk_usage.py`: the script behind `disk_usage`.

The `rag` server needs the index: run `uv run --python 3.12 --no-project --with chroma-mcp python rag/build_chroma.py` from the W4 folder first.
