import { Plugin } from "@opencode/plugin"
import { execFile } from "node:child_process"
import { promisify } from "node:util"
import path from "node:path"

// OpenCode 2.x custom tool that runs a Python script.
// Copy this file to .opencode/plugins/ and disk_usage.py to .opencode/, then restart OpenCode.
// The model only sees the description and the arguments. The Python script does the work.
const run = promisify(execFile)

export default Plugin.define({
  id: "w4.disk-usage",
  async setup(ctx) {
    const folder = ctx.location.directory
    await ctx.tool.transform((editor) => {
      editor.add({
        name: "disk_usage",
        description: "This tool returns the % of disk usage on a given server. Use when asked to check disk usage.",
        input: {
          type: "object",
          properties: { host: { type: "string", description: "The host, for example db-prd-02" } },
          required: ["host"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input) => {
          const { host } = input as { host: string }
          const script = path.join(folder, ".opencode", "disk_usage.py")
          try {
            const { stdout } = await run(process.platform === "win32" ? "python" : "python3", [script, host], { cwd: folder, timeout: 10_000 })
            return { content: stdout.trim() }
          } catch (error) {
            return { content: `Error: the script did not run (${(error as Error).message.split("\n")[0]}).` }
          }
        },
      })
    })
  },
})
