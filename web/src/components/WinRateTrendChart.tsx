import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface DataPoint {
  month: string;
  winRate: number;
  wins: number;
  played: number;
}

interface Props {
  data: DataPoint[];
}

function formatMonth(yyyyMm: string): string {
  const [year, month] = yyyyMm.split("-");
  const date = new Date(Number(year), Number(month) - 1, 1);
  return date.toLocaleString("en-US", { month: "short", year: "2-digit" });
}

export function WinRateTrendChart({ data }: Props) {
  if (data.length < 3) return null;

  const chartData = data.map((d) => ({
    label: formatMonth(d.month),
    winRate: Math.round(d.winRate * 100),
    wins: d.wins,
    played: d.played,
  }));

  return (
    <ResponsiveContainer width="100%" height={160}>
      <LineChart data={chartData} margin={{ top: 4, right: 8, bottom: 4, left: -20 }}>
        <XAxis dataKey="label" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
        <Tooltip
          formatter={(value) => [`${Number(value)}%`, "Win rate"]}
          contentStyle={{
            fontSize: 12,
            background: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
          }}
          labelStyle={{ color: "hsl(var(--foreground))" }}
        />
        <Line
          type="monotone"
          dataKey="winRate"
          stroke="hsl(var(--primary))"
          strokeWidth={2}
          dot={{ r: 3, fill: "hsl(var(--primary))" }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
