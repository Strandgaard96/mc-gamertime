import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../lib/api";
import { AuthProvider } from "../lib/AuthContext";
import { LogResultDialog } from "./LogResultDialog";

vi.mock("../lib/api");

beforeEach(() => {
  vi.mocked(api.getGames).mockResolvedValue([]);
  vi.mocked(api.getUsers).mockResolvedValue([]);
  vi.mocked(api.getCurrentUser).mockResolvedValue({
    sub: "bob",
    role: "readonly",
    displayName: "Bob",
  });
});

describe("LogResultDialog", () => {
  it("does not fetch the admin-only user list while closed", async () => {
    // Mounted once per game card, for every viewer: a readonly user would get
    // a 403 from GET /users for each card if the query ran while closed.
    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={qc}>
        <AuthProvider>
          <LogResultDialog open={false} onClose={() => {}} defaultGameId="g1" />
          <LogResultDialog open={false} onClose={() => {}} defaultGameId="g2" />
        </AuthProvider>
      </QueryClientProvider>,
    );
    await vi.waitFor(() => expect(api.getGames).toHaveBeenCalled());
    expect(api.getUsers).not.toHaveBeenCalled();
  });
});
