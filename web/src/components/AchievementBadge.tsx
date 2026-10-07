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
            : // Locked: dashed outline signals "not yet", text stays readable — a whole-card
              // opacity-50 dropped it below 3:1, and the hover tooltip never reaches touch.
              "bg-muted/20 border-dashed border-border text-muted-foreground"
        }`}
      >
        {earned ? (
          <span className="text-2xl">{icon}</span>
        ) : (
          <Lock size={22} className="text-muted-foreground opacity-60" aria-hidden="true" />
        )}
        <span className="text-xs font-medium leading-tight">{achievement.label}</span>
        {earned ? (
          <span className="text-xs text-muted-foreground">{formatDate(achievement.earnedAt!)}</span>
        ) : (
          <span className="text-[11px] leading-snug text-muted-foreground line-clamp-2">
            {achievement.description}
          </span>
        )}
      </div>
    </Tooltip>
  );
}
