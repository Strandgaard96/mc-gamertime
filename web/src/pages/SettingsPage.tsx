import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Settings as SettingsIcon } from "lucide-react";
import { type FormEvent, useEffect, useState } from "react";
import { toast } from "sonner";
import { PageTransition } from "../components/PageTransition";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { getSettings, updateSettings } from "../lib/api";
import type { AdminSettings } from "../lib/types";

function BrandingCard({ data }: { data: AdminSettings | undefined }) {
  const qc = useQueryClient();
  const [displayName, setDisplayName] = useState("");

  useEffect(() => {
    if (data) setDisplayName(data.displayName);
  }, [data]);

  const trimmed = displayName.trim();
  const validationError =
    trimmed.length === 0
      ? "Display name is required"
      : trimmed.length > 60
        ? "Display name must be 60 characters or fewer"
        : null;
  const isDirty = data !== undefined && displayName !== data.displayName;

  const saveMutation = useMutation({
    mutationFn: updateSettings,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["settings"] });
      toast.success("Branding saved");
    },
    onError: (err) =>
      toast.error(err instanceof Error && err.message ? err.message : "Failed to save branding"),
  });

  function handleSave(e: FormEvent) {
    e.preventDefault();
    if (validationError) return;
    saveMutation.mutate({ displayName: trimmed });
  }

  return (
    <form onSubmit={handleSave} className="space-y-3 rounded-lg border bg-card p-4">
      <h2 className="font-semibold">Branding</h2>
      <div className="space-y-1.5">
        <label className="text-sm font-medium" htmlFor="displayName">
          Instance Display Name
        </label>
        <Input
          id="displayName"
          placeholder="MC GamerTime"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
        />
        {validationError && <p className="text-sm text-destructive">{validationError}</p>}
      </div>
      <div className="flex justify-end">
        <Button type="submit" disabled={!isDirty || !!validationError || saveMutation.isPending}>
          {saveMutation.isPending ? "Saving…" : "Save"}
        </Button>
      </div>
    </form>
  );
}

function IntegrationsCard({ data }: { data: AdminSettings | undefined }) {
  const qc = useQueryClient();
  const [bggToken, setBggToken] = useState("");

  const saveMutation = useMutation({
    mutationFn: updateSettings,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["settings"] });
      setBggToken("");
      toast.success("BGG token saved");
    },
    onError: (err) =>
      toast.error(
        err instanceof Error && err.message ? err.message : "Failed to save the BGG token",
      ),
  });

  function handleSave(e: FormEvent) {
    e.preventDefault();
    if (!bggToken) return;
    saveMutation.mutate({ bggToken });
  }

  function handleClearToken() {
    if (
      !window.confirm(
        "Clear the BGG API token? Game search will be disabled until a new one is set.",
      )
    )
      return;
    saveMutation.mutate({ bggToken: null });
  }

  return (
    <form onSubmit={handleSave} className="space-y-3 rounded-lg border bg-card p-4">
      <h2 className="font-semibold">Integrations</h2>
      <div className="space-y-1.5">
        <label className="text-sm font-medium" htmlFor="bggToken">
          BGG API Token
        </label>
        <Input
          id="bggToken"
          type="password"
          placeholder={data?.bggTokenSet ? "Token is configured" : "No token set"}
          value={bggToken}
          onChange={(e) => setBggToken(e.target.value)}
        />
        {data?.bggTokenSet && (
          <button
            type="button"
            onClick={handleClearToken}
            className="text-sm text-destructive hover:underline"
          >
            Clear token
          </button>
        )}
      </div>
      <div className="flex justify-end">
        <Button type="submit" disabled={!bggToken || saveMutation.isPending}>
          {saveMutation.isPending ? "Saving…" : "Save"}
        </Button>
      </div>
    </form>
  );
}

function InstanceUrlCard({ data }: { data: AdminSettings | undefined }) {
  const qc = useQueryClient();
  const [appBaseUrl, setAppBaseUrl] = useState("");

  useEffect(() => {
    if (data) setAppBaseUrl(data.appBaseUrl ?? "");
  }, [data]);

  const isDirty = data !== undefined && appBaseUrl !== (data.appBaseUrl ?? "");

  const saveMutation = useMutation({
    mutationFn: updateSettings,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["settings"] });
      toast.success("Instance URL saved");
    },
    onError: (err) =>
      toast.error(
        err instanceof Error && err.message ? err.message : "Failed to save the instance URL",
      ),
  });

  function handleSave(e: FormEvent) {
    e.preventDefault();
    saveMutation.mutate({ appBaseUrl: appBaseUrl.trim() || null });
  }

  const placeholder = data?.appBaseUrlEnvFallback
    ? `Using env: ${data.appBaseUrlEnvFallback}`
    : "e.g. https://games.example.com";

  return (
    <form onSubmit={handleSave} className="space-y-3 rounded-lg border bg-card p-4">
      <h2 className="font-semibold">Instance URL</h2>
      <div className="space-y-1.5">
        <label className="text-sm font-medium" htmlFor="appBaseUrl">
          Public Base URL
        </label>
        <Input
          id="appBaseUrl"
          placeholder={placeholder}
          value={appBaseUrl}
          onChange={(e) => setAppBaseUrl(e.target.value)}
        />
        <p className="text-sm text-muted-foreground">
          Used to build links in password-reset emails. Leave blank to use the server's{" "}
          <code>APP_BASE_URL</code> environment variable.
        </p>
      </div>
      <div className="flex justify-end">
        <Button type="submit" disabled={!isDirty || saveMutation.isPending}>
          {saveMutation.isPending ? "Saving…" : "Save"}
        </Button>
      </div>
    </form>
  );
}

export default function SettingsPage() {
  const { data, isLoading } = useQuery<AdminSettings>({
    queryKey: ["settings", "admin"],
    queryFn: getSettings,
  });

  if (isLoading) return <p className="text-muted-foreground p-6">Loading…</p>;

  return (
    <PageTransition>
      <div className="max-w-2xl mx-auto p-4 md:p-6">
        <h1 className="text-2xl font-display font-bold flex items-center gap-2 mb-6">
          <SettingsIcon size={24} className="text-primary" />
          Settings
        </h1>
        <div className="space-y-4">
          <BrandingCard data={data} />
          <IntegrationsCard data={data} />
          <InstanceUrlCard data={data} />
        </div>
      </div>
    </PageTransition>
  );
}
