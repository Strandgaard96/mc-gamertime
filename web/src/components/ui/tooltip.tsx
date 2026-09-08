import { HelpCircle } from "lucide-react";
import { type ReactNode, useState } from "react";

interface TooltipProps {
  text: string;
  children?: ReactNode;
  fullWidth?: boolean;
}

export function Tooltip({ text, children, fullWidth }: TooltipProps) {
  const [isVisible, setVisible] = useState(false);

  return (
    <div className={`relative ${fullWidth ? "block w-full" : "inline-block"}`}>
      <div
        className={fullWidth ? "block w-full" : "inline-block"}
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
      >
        {children ?? (
          <HelpCircle
            size={12}
            className="text-muted-foreground hover:text-primary cursor-help transition-colors"
          />
        )}
      </div>
      {isVisible && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-popover text-popover-foreground text-xs rounded shadow-lg text-center z-50 border border-border pointer-events-none">
          {text}
        </div>
      )}
    </div>
  );
}
