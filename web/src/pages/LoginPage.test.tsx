import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "../lib/AuthContext";
import * as api from "../lib/api";
import LoginPage from "./LoginPage";

vi.mock("../lib/api");

function renderLoginPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.mocked(api.getCurrentUser).mockRejectedValue(new Error("not logged in"));
});

describe("LoginPage", () => {
  it("logs in and redirects on valid credentials", async () => {
    const user = userEvent.setup();
    vi.mocked(api.login).mockResolvedValue({
      username: "alice",
      displayName: "Alice",
      role: "admin",
    } as any);

    renderLoginPage();

    await user.type(screen.getByLabelText("Username"), "alice");
    await user.type(screen.getByLabelText("Password"), "secret");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => expect(api.login).toHaveBeenCalledWith("alice", "secret"));
  });

  it("shows a rate-limit message on 429", async () => {
    const user = userEvent.setup();
    vi.mocked(api.login).mockRejectedValue({ status: 429, retryAfter: 30 });

    renderLoginPage();

    await user.type(screen.getByLabelText("Username"), "alice");
    await user.type(screen.getByLabelText("Password"), "wrong");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText(/try again in 30 seconds/i)).toBeInTheDocument();
  });

  it("shows invalid-credentials message when the API is healthy", async () => {
    const user = userEvent.setup();
    vi.mocked(api.login).mockRejectedValue({ status: 401 });
    vi.mocked(api.checkHealth).mockResolvedValue(true);

    renderLoginPage();

    await user.type(screen.getByLabelText("Username"), "alice");
    await user.type(screen.getByLabelText("Password"), "wrong");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Invalid username or password")).toBeInTheDocument();
  });
});
