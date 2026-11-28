// Hidden outcome check (keep outside the agent's workspace). Run with TZ=America/New_York.
// Defect 2: a date-only birth date must give the right age on the day before a birthday.
import { describe, it, expect, vi, afterEach } from "vitest";
import { buildValidatorUserPrompt } from "@/lib/astrology/prompts/validator";
import type { NatalChart } from "@/lib/profile";

afterEach(() => vi.useRealTimers());

const chart: NatalChart = {
  ascendant: { sign: "Leo", sign_num: 4, degree: 12.5, abs_pos: 132.5 },
  planets: {},
  moon_nakshatra: { num: 7, name: "Pushya", pada: 1, lord: "Saturn" },
};

describe("defect 2: age in US time zones", () => {
  it("is 35 the day before a 36th birthday (born 1990-06-15, today 2026-06-14 local)", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date(2026, 5, 14, 12, 0, 0));
    const prompt = buildValidatorUserPrompt(chart, "1990-06-15");
    expect(prompt).toContain("current age: 35 years old");
  });

  it("is 36 on the birthday itself", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date(2026, 5, 15, 12, 0, 0));
    const prompt = buildValidatorUserPrompt(chart, "1990-06-15");
    expect(prompt).toContain("current age: 36 years old");
  });
});
