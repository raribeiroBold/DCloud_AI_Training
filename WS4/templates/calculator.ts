import { Plugin } from "@opencode/plugin"

// OpenCode 2.x custom tool: a plugin that registers one tool.
// Copy this file to .opencode/plugins/ and restart OpenCode.
// You only write the description. The code below does the arithmetic exactly.
export default Plugin.define({
  id: "w4.calculator",
  async setup(ctx) {
    await ctx.tool.transform((editor) => {
      editor.add({
        name: "calculator",
        description: "WRITE ME: what this tool does, and when the agent must use it.",
        input: {
          type: "object",
          properties: {
            a: { type: "number", description: "The first number" },
            op: { type: "string", enum: ["add", "subtract", "multiply", "divide"], description: "The operation" },
            b: { type: "number", description: "The second number" },
          },
          required: ["a", "op", "b"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input) => {
          const { a, op, b } = input as { a: number; op: string; b: number }
          if (op === "divide" && b === 0) return { content: "Error: division by zero." }
          const result = op === "add" ? a + b : op === "subtract" ? a - b : op === "multiply" ? a * b : a / b
          return { content: String(result) }
        },
      })
    })
  },
})
