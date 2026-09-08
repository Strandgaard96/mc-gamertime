import { AlertTriangle } from "lucide-react";
import type { FallbackProps } from "react-error-boundary";
import { Button } from "../components/ui/button";

export function ErrorPage({ error, resetErrorBoundary }: FallbackProps) {
  const message = error instanceof Error ? error.message : String(error);
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-4 text-center">
      <AlertTriangle size={48} className="text-destructive" />
      <h1 className="text-xl font-display font-semibold">Something went wrong</h1>
      <p className="text-sm text-muted-foreground max-w-sm">{message}</p>
      <Button onClick={resetErrorBoundary}>Try again</Button>
    </div>
  );
}
