// Hidden outcome check (keep outside the agent's workspace).
// Defect 1: a failed profile write must not report success.
import { describe, it, expect } from "vitest";
import { pushSync } from "@/lib/sync-push";

const admin = {
  rpc: async () => ({ data: null, error: { code: "PGRST202", message: "Could not find the function" } }),
  from: (table: string) => ({
    upsert: async () => ({ error: table === "user_profiles" ? { message: "permission denied" } : null }),
    select: () => ({ eq: async () => ({ data: [], error: null }) }),
    insert: async () => ({ error: null }),
    delete: () => ({ eq: () => ({ in: async () => ({ error: null }) }) }),
  }),
} as never;

describe("defect 1: failed profile write", () => {
  it("does not report success", async () => {
    await expect(pushSync(admin, { userId: "u1", profileRow: { chart: {} }, observations: [] })).rejects.toBeTruthy();
  });
});
