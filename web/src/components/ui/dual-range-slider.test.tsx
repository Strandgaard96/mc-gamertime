import { fireEvent, render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DualRangeSlider } from "./dual-range-slider";

function renderSlider(value: [number, number], onChange = vi.fn()) {
  const utils = render(<DualRangeSlider min={0} max={100} value={value} onChange={onChange} />);
  const [lo, hi] = Array.from(utils.container.querySelectorAll<HTMLInputElement>("input"));
  return { ...utils, lo, hi, onChange };
}

describe("DualRangeSlider", () => {
  it("renders two range inputs bound to the low and high values", () => {
    const { lo, hi } = renderSlider([20, 80]);

    expect(lo.type).toBe("range");
    expect(hi.type).toBe("range");
    expect(lo.value).toBe("20");
    expect(hi.value).toBe("80");
    expect(lo).toHaveAttribute("min", "0");
    expect(hi).toHaveAttribute("max", "100");
  });

  it("positions the filled track between the two thumbs", () => {
    const { container } = renderSlider([25, 75]);

    const fill = container.querySelector<HTMLElement>(".bg-primary");
    expect(fill?.style.left).toBe("25%");
    expect(fill?.style.width).toBe("50%");
  });

  it("emits the new low value when the low thumb moves", () => {
    const { lo, onChange } = renderSlider([20, 80]);

    fireEvent.change(lo, { target: { value: "40" } });

    expect(onChange).toHaveBeenCalledWith([40, 80]);
  });

  it("emits the new high value when the high thumb moves", () => {
    const { hi, onChange } = renderSlider([20, 80]);

    fireEvent.change(hi, { target: { value: "60" } });

    expect(onChange).toHaveBeenCalledWith([20, 60]);
  });

  it("clamps the low thumb so it cannot cross above the high thumb", () => {
    const { lo, onChange } = renderSlider([20, 50]);

    fireEvent.change(lo, { target: { value: "90" } });

    expect(onChange).toHaveBeenCalledWith([50, 50]);
  });

  it("clamps the high thumb so it cannot cross below the low thumb", () => {
    const { hi, onChange } = renderSlider([40, 80]);

    fireEvent.change(hi, { target: { value: "10" } });

    expect(onChange).toHaveBeenCalledWith([40, 40]);
  });

  it("passes the step through to both inputs", () => {
    const { container } = render(
      <DualRangeSlider min={1} max={5} step={0.5} value={[1, 5]} onChange={vi.fn()} />,
    );

    const inputs = container.querySelectorAll("input");
    expect(inputs[0]).toHaveAttribute("step", "0.5");
    expect(inputs[1]).toHaveAttribute("step", "0.5");
  });
});
