// web/src/pages/ForgotPasswordPage.tsx
import { Dices } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { PageTransition } from "../components/PageTransition";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { forgotPassword } from "../lib/api";

export default function ForgotPasswordPage() {
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await forgotPassword(username);
    } finally {
      // Always show the same confirmation, win or lose — the backend
      // intentionally never reveals whether the username exists.
      setLoading(false);
      setSubmitted(true);
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
            <p className="text-muted-foreground mt-2">Reset your password</p>
          </div>
          {submitted ? (
            <p className="text-sm text-center text-muted-foreground">
              If that account exists and has an email on file, a reset link is on its way. Check the
              server logs if no SMTP server is configured.
            </p>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                required
              />
              <Button type="submit" className="w-full" isLoading={loading}>
                Send reset link
              </Button>
            </form>
          )}
          <p className="text-sm text-center">
            <Link to="/login" className="text-primary hover:underline">
              Back to sign in
            </Link>
          </p>
        </div>
      </div>
    </PageTransition>
  );
}
