// web/src/pages/ResetPasswordPage.tsx
import { Dices } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { PageTransition } from "../components/PageTransition";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { resetPassword } from "../lib/api";

export default function ResetPasswordPage() {
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") ?? "";

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await resetPassword(token, newPassword);
      toast.success("Password updated — please sign in");
      navigate("/login");
    } catch {
      setError("That reset link is invalid or has expired — request a new one.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageTransition>
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <div className="w-full max-w-sm space-y-6">
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Dices size={28} className="text-primary" />
              <span className="text-3xl font-display font-bold text-primary">MC GamerTime</span>
            </div>
            <p className="text-muted-foreground mt-2">Choose a new password</p>
          </div>
          {token ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                type="password"
                placeholder="New password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                autoComplete="new-password"
                required
                minLength={8}
              />
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" isLoading={loading} disabled={!token}>
                Update password
              </Button>
            </form>
          ) : (
            <p className="text-sm text-center text-muted-foreground">
              This reset link is missing or invalid. Request a new one.
            </p>
          )}
          <p className="text-sm text-center">
            <Link to="/forgot-password" className="text-primary hover:underline">
              Back to forgot password
            </Link>
          </p>
        </div>
      </div>
    </PageTransition>
  );
}
