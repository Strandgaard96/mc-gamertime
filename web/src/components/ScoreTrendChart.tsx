import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface DataPoint {
  month: string;
  avgScore: number;
}

interface Props {
  data: DataPoint[];
}

function formatMonth(yyyyMm: string): string {
  const [year, month] = yyyyMm.split("-");
  const date = new Date(Number(year), Number(month) - 1, 1);
  return date.toLocaleString("en-US", { month: "short", year: "2-digit" });
}

export function ScoreTrendChart({ data }: Props) {
  if (data.length < 2) return null;

  const chartData = data.map((d) => ({
    label: formatMonth(d.month),
    avgScore: Math.round(d.avgScore * 10) / 10,
  }));

  return (
    <ResponsiveContainer width="100%" height={160}>
      <LineChart data={chartData} margin={{ top: 4, right: 8, bottom: 4, left: -20 }}>
        <XAxis dataKey="label" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 10]} tick={{ fontSize: 11 }} />
        <Tooltip
          formatter={(value) => [value, "Avg score"]}
          contentStyle={{
            fontSize: 12,
            background: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
          }}
          labelStyle={{ color: "hsl(var(--foreground))" }}
        />
        <Line
          type="monotone"
          dataKey="avgScore"
          stroke="hsl(var(--primary))"
          strokeWidth={2}
          dot={{ r: 3, fill: "hsl(var(--primary))" }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
