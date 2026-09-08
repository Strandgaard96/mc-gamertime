import { Skeleton } from "./ui/skeleton";

export function GameCardSkeleton() {
  return (
    <div className="bg-card rounded-lg border overflow-hidden">
      <Skeleton className="h-40 w-full rounded-none" />

      <div className="p-3 space-y-2">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
      </div>
    </div>
  );
}
