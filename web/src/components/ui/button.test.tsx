import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createRef } from "react";
import { MemoryRouter, Link } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { Button } from "./button";

describe("Button", () => {
  it("renders a native button and forwards clicks", async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Save</Button>);

    const btn = screen.getByRole("button", { name: "Save" });
    expect(btn.tagName).toBe("BUTTON");
    await user.click(btn);

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("applies variant and size classes", () => {
    render(
      <Button variant="destructive" size="sm">
        Delete
      </Button>,
    );

    const btn = screen.getByRole("button", { name: "Delete" });
    expect(btn).toHaveClass("bg-destructive", "h-9", "px-3");
    expect(btn).not.toHaveClass("bg-primary", "h-10");
  });

  it("lets a caller's className override conflicting defaults", () => {
    render(<Button className="h-12">Tall</Button>);

    const btn = screen.getByRole("button", { name: "Tall" });
    expect(btn).toHaveClass("h-12");
    expect(btn).not.toHaveClass("h-10");
  });

  it("disables the button and shows a spinner while loading", async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    const { container } = render(
      <Button isLoading onClick={onClick}>
        Saving
      </Button>,
    );

    const btn = screen.getByRole("button", { name: "Saving" });
    expect(btn).toBeDisabled();
    expect(container.querySelector(".animate-spin")).not.toBeNull();

    await user.click(btn);
    expect(onClick).not.toHaveBeenCalled();
  });

  it("does not render a spinner when not loading", () => {
    const { container } = render(<Button>Idle</Button>);

    expect(container.querySelector(".animate-spin")).toBeNull();
    expect(screen.getByRole("button", { name: "Idle" })).toBeEnabled();
  });

  it("respects an explicit disabled prop", () => {
    render(<Button disabled>Nope</Button>);
    expect(screen.getByRole("button", { name: "Nope" })).toBeDisabled();
  });

  it("with asChild renders the child element instead of a button, merging classes", () => {
    render(
      <MemoryRouter>
        <Button asChild variant="outline" className="w-full">
          <Link to="/games" className="underline">
            Browse
          </Link>
        </Button>
      </MemoryRouter>,
    );

    const link = screen.getByRole("link", { name: "Browse" });
    expect(link.tagName).toBe("A");
    expect(link).toHaveAttribute("href", "/games");
    expect(link).toHaveClass("border", "w-full", "underline", "inline-flex");
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("with asChild forwards extra props and the ref to the child", () => {
    const ref = createRef<HTMLButtonElement>();
    render(
      <Button asChild ref={ref} aria-label="Go home">
        <a href="/">Home</a>
      </Button>,
    );

    const link = screen.getByRole("link", { name: "Go home" });
    expect(ref.current).toBe(link);
  });

  it("falls back to a real button when asChild is set but the child is not an element", () => {
    render(<Button asChild>plain text</Button>);

    expect(screen.getByRole("button", { name: "plain text" })).toBeInTheDocument();
  });
});
