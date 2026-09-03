import { Lock } from "lucide-react";
import type { Achievement } from "../lib/types";
import { formatDate } from "../lib/utils";
import { Tooltip } from "./ui/tooltip";

interface Props {
  achievement: Achievement;
}

export function AchievementBadge({ achievement }: Props) {
  const earned = achievement.earnedAt !== null;
  const icon = achievement.icon ?? "🏅";
  const tooltipText = earned
    ? `${achievement.description} — earned ${formatDate(achievement.earnedAt!)}`
    : achievement.description;

  return (
    <Tooltip text={tooltipText} fullWidth>
      <div
        className={`flex flex-col items-center gap-1 p-3 rounded-lg border transition-colors text-center cursor-default w-full h-full ${
          earned
            ? "bg-primary/10 border-primary/30 text-foreground"
            : "bg-muted/30 border-border text-muted-foreground opacity-50"
        }`}
      >
        {earned ? (
          <span className="text-2xl">{icon}</span>
        ) : (
          <Lock size={22} className="text-muted-foreground" />
        )}
        <span className="text-xs font-medium leading-tight">{achievement.label}</span>
        {earned && (
          <span className="text-xs text-muted-foreground">{formatDate(achievement.earnedAt!)}</span>
        )}
      </div>
    </Tooltip>
  );
}
