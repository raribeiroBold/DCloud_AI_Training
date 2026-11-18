import { Plugin } from "@opencode/plugin"

// OpenCode 2.x guard: a plugin that runs before every tool call, for every agent.
// Copy this file to .opencode/plugins/ and restart OpenCode.
// You only edit PROTECTED. The code below blocks any shell command that
// deletes, moves or truncates something whose path contains a protected name.
const PROTECTED: string[] = ["WRITE ME"] // <== the only line you edit
const CHANGES = /\b(rm|unlink|truncate|shred|mv|del|Remove-Item)\b|-delete\b/

export default Plugin.define({
  id: "w4.guard",
  async setup(ctx) {
    await ctx.tool.hook("execute.before", (event) => {
      if (event.tool !== "shell" && event.tool !== "bash") return
      const command = String((event.input as { command?: unknown }).command ?? "")
      const target = PROTECTED.find((name) => command.includes(name))
      if (target && CHANGES.test(command))
        throw new Error(`guard: changing ${target} is blocked. Report this to a person and stop.`)
    })
  },
})
