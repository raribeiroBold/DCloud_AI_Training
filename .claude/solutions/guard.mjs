// Claude Code guard: a PreToolUse hook. WS4/.claude/settings.json runs it.
// Claude Code runs it before every tool call it matches, for the main agent and its subagents,
// and before the permission ask. Exit code 2 blocks the call; Claude reads the message.
// You only edit PROTECTED. The code below blocks any shell command that deletes, moves or
// truncates something whose path contains a protected name, and any write into 4_Archive.
const PROTECTED = ["pg_wal"] // <== the only line you edit
const CHANGES = /\b(rm|unlink|truncate|shred|mv|del|Remove-Item)\b|-delete\b/
const ARCHIVE = /(^|[\\/])4_Archive([\\/]|$)/
const WRITES = /^(Write|Edit|MultiEdit|NotebookEdit|mcp__vault__(write_file|edit_file|create_directory|move_file|append_file|copy_file))$/

function block(message) {
  process.stderr.write(message + "\n")
  process.exit(2)
}

let raw = ""
process.stdin.setEncoding("utf8")
process.stdin.on("data", (chunk) => (raw += chunk))
process.stdin.on("end", () => {
  let event
  try {
    event = JSON.parse(raw)
  } catch {
    block("guard: could not read the tool call, so it is blocked. Report this to a person and stop.")
  }
  const tool = String(event.tool_name ?? "")
  const input = event.tool_input ?? {}

  if (tool === "Bash" || tool === "PowerShell") {
    const command = String(input.command ?? "")
    const target = PROTECTED.find((name) => command.includes(name))
    if (target && CHANGES.test(command)) block(`guard: changing ${target} is blocked. Report this to a person and stop.`)
  }

  if (WRITES.test(tool)) {
    const paths = [input.file_path, input.notebook_path, input.path, input.source, input.destination]
      .filter(Boolean)
      .map(String)
    if (paths.some((p) => ARCHIVE.test(p))) block("guard: 4_Archive is read-only. Report this to a person and stop.")
  }

  process.exit(0)
})
