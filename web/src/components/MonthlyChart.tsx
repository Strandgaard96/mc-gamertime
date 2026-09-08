import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { PerMonth } from "../lib/types";

interface Props {
  data: PerMonth[];
}

export function MonthlyChart({ data }: Props) {
  if (data.length === 0)
    return <p className="text-muted-foreground text-sm">No game sessions recorded yet.</p>;

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data}>
        <XAxis dataKey="month" tick={{ fontSize: 11 }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey="count" name="Sessions" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
