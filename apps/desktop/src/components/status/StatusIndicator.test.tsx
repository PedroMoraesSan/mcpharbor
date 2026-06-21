import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusIndicator } from "@/components/status/StatusIndicator";

describe("StatusIndicator", () => {
  it("renders running status", () => {
    render(<StatusIndicator status="running" />);
    expect(screen.getByText("Running")).toBeInTheDocument();
  });

  it("renders stopped status", () => {
    render(<StatusIndicator status="stopped" />);
    expect(screen.getByText("Stopped")).toBeInTheDocument();
  });

  it("renders error status", () => {
    render(<StatusIndicator status="error" />);
    expect(screen.getByText("Error")).toBeInTheDocument();
  });
});
