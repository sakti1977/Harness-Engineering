// Held-out check for defect 4 (pretty-printed JSON from Claude must parse).
import { describe, it, expect } from "vitest";
import { prepareJsonString } from "./claude-json";

describe("defect 4: pretty-printed JSON survives prepareJsonString", () => {
  it("keeps structural whitespace and escapes control chars only inside strings", () => {
    const raw = '```json\n{\n  "summary": "first line\nsecond line",\n  "items": [\n    1,\n    2\n  ]\n}\n```';
    const parsed = JSON.parse(prepareJsonString(raw));
    expect(parsed).toEqual({ summary: "first line\nsecond line", items: [1, 2] });
  });
});
