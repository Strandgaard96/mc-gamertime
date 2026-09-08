import { Dices } from "lucide-react";

export function PageSkeleton() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <Dices size={40} className="text-primary animate-spin" />
    </div>
  );
}
