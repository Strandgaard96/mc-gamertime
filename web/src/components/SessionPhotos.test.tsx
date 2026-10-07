import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../lib/api";
import { AuthProvider } from "../lib/AuthContext";
import type { PhotoItem } from "../lib/types";
import { SessionPhotos } from "./SessionPhotos";

vi.mock("../lib/api");

const photo = (pk: string, uploaderId: string): PhotoItem => ({
  pk,
  type: "photo",
  sessionPk: "s1",
  key: `session-photos/${pk}.webp`,
  imageUrl: `/session-photos/${pk}.webp`,
  uploaderId,
  uploaderName: uploaderId,
  createdAt: "2026-06-01T00:00:00Z",
});

function renderAs(sub: string, role: "admin" | "readonly", items: PhotoItem[]) {
  vi.mocked(api.getCurrentUser).mockResolvedValue({ sub, role, displayName: sub });
  vi.mocked(api.getReactions).mockResolvedValue(items);
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <AuthProvider>
        <SessionPhotos sessionPk="s1" />
      </AuthProvider>
    </QueryClientProvider>,
  );
}

beforeEach(() => vi.clearAllMocks());

describe("SessionPhotos", () => {
  it("shows Add photo below the cap", async () => {
    renderAs("bob", "readonly", [photo("p1", "alice")]);
    expect(await screen.findByRole("button", { name: /add photo/i })).toBeInTheDocument();
  });

  it("hides Add photo at 6", async () => {
    renderAs("bob", "readonly", ["1", "2", "3", "4", "5", "6"].map((i) => photo(`p${i}`, "alice")));
    await screen.findAllByRole("img");
    expect(screen.queryByRole("button", { name: /add photo/i })).not.toBeInTheDocument();
  });

  it("only shows delete for own photos unless admin", async () => {
    renderAs("bob", "readonly", [photo("p1", "alice"), photo("p2", "bob")]);
    await screen.findAllByRole("img");
    expect(screen.getAllByRole("button", { name: /delete photo/i })).toHaveLength(1);
  });

  it("admin can delete any photo", async () => {
    renderAs("root", "admin", [photo("p1", "alice"), photo("p2", "bob")]);
    await screen.findAllByRole("img");
    expect(screen.getAllByRole("button", { name: /delete photo/i })).toHaveLength(2);
  });
});
