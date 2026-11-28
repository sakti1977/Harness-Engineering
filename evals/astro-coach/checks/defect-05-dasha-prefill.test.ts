// Held-out check for defect 5: the dasha request must end with a user message.
import { describe, it, expect, vi } from "vitest";

const { create } = vi.hoisted(() => ({
  create: vi.fn(async () => ({
    content: [{ type: "text", text: '{"themes":["a"]}' }],
    usage: { input_tokens: 1, output_tokens: 1 },
  })),
}));

vi.mock("@anthropic-ai/sdk", () => ({
  default: class {
    messages = { create };
  },
}));
vi.mock("@/lib/llm-usage", () => ({
  recordLlmUsage: () => {},
  createStreamUsageTracker: () => ({}),
}));

import { generateDashaPrediction } from "./claude";

describe("defect 5: dasha prediction request", () => {
  it("does not end the conversation with an assistant message, and returns the model text", async () => {
    const out = await generateDashaPrediction("prompt");
    const args = create.mock.calls[0][0] as { messages: { role: string }[] };
    expect(args.messages[args.messages.length - 1].role).toBe("user");
    expect(out).toBe('{"themes":["a"]}');
  });
});
