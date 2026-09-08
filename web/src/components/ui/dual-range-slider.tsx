const thumbClasses =
  "[&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-background [&::-webkit-slider-thumb]:cursor-pointer " +
  "[&::-moz-range-thumb]:pointer-events-auto [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-primary [&::-moz-range-thumb]:border-2 [&::-moz-range-thumb]:border-background [&::-moz-range-thumb]:cursor-pointer";

interface Props {
  min: number;
  max: number;
  step?: number;
  value: [number, number];
  onChange: (value: [number, number]) => void;
}

export function DualRangeSlider({ min, max, step = 1, value, onChange }: Props) {
  const [lo, hi] = value;

  const leftPct = ((lo - min) / (max - min)) * 100;
  const widthPct = ((hi - lo) / (max - min)) * 100;

  return (
    <div className="relative h-5 flex items-center">
      <div className="absolute inset-x-0 h-1.5 rounded-full bg-muted" />
      <div
        className="absolute h-1.5 rounded-full bg-primary"
        style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
      />
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={lo}
        onChange={(e) => onChange([Math.min(+e.target.value, hi), hi])}
        className={`absolute inset-x-0 w-full h-5 appearance-none bg-transparent pointer-events-none ${thumbClasses}`}
      />
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={hi}
        onChange={(e) => onChange([lo, Math.max(+e.target.value, lo)])}
        className={`absolute inset-x-0 w-full h-5 appearance-none bg-transparent pointer-events-none ${thumbClasses}`}
      />
    </div>
  );
}
