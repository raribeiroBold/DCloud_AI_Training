import { Plugin } from "@opencode/plugin"
import { mkdir, writeFile } from "node:fs/promises"
import path from "node:path"

// OpenCode 2.x custom tool: writes a ticket DRAFT to tickets/. Nothing is sent to JSM.
// Copy this file to .opencode/plugins/ and restart OpenCode.
// You write the description. Its permission is "ask" in opencode.json ("create_ticket").
export default Plugin.define({
  id: "w4.create-ticket",
  async setup(ctx) {
    const folder = ctx.location.directory
    await ctx.tool.transform((editor) => {
      editor.add({
        name: "create_ticket",
        description: "WRITE ME: what this tool does, and when the agent may use it.",
        input: {
          type: "object",
          properties: {
            host: { type: "string", description: "The host, for example db-prd-02" },
            priority: { type: "string", enum: ["P1", "P2", "P3", "P4"], description: "P1 critical, P2 high, P3 medium, P4 low" },
            summary: { type: "string", description: "One line that says what is wrong" },
            evidence: { type: "string", description: "The log lines or runbook section that support it" },
          },
          required: ["host", "priority", "summary", "evidence"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input) => {
          const args = input as { host: string; priority: string; summary: string; evidence: string }
          const host = args.host.replace(/[^A-Za-z0-9._-]/g, "_")
          const dir = path.join(folder, "tickets")
          await mkdir(dir, { recursive: true })
          const name = `${new Date().toISOString().replace(/[:.]/g, "-")}-${host}.md`
          const body = [`# ${args.summary}`, "", `- Host: ${host}`, `- Priority: ${args.priority}`,
            "- Status: draft, not sent to JSM", "", "## Evidence", "", args.evidence, ""].join("\n")
          await writeFile(path.join(dir, name), body)
          return { content: `Draft written to tickets/${name}` }
        },
      })
    })
  },
})
