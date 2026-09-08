import { ChevronLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { PageTransition } from "../components/PageTransition";
import { TiptapEditor } from "../components/TiptapEditor";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { useRecommendedDetail, useUpdateRecommended } from "../hooks/useRecommended";

export default function RecEditorPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: rec, isLoading } = useRecommendedDetail(id);
  const updateRec = useUpdateRecommended();
  const [content, setContent] = useState("");
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (rec && !initialized) {
      setContent(rec.content ?? "");
      setInitialized(true);
    }
  }, [rec, initialized]);

  async function handleSave() {
    if (!id) return;
    await updateRec.mutateAsync({ id, data: { content } });
    navigate("/admin/recommended");
  }

  return (
    <PageTransition>
      <div className="flex flex-col h-dvh bg-background">
        <div className="flex items-center justify-between border-b px-4 py-3 bg-card shrink-0">
          <div className="flex items-center gap-3">
            <Link
              to="/admin/recommended"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <ChevronLeft size={20} />
            </Link>
            {isLoading ? (
              <Skeleton className="h-6 w-40" />
            ) : (
              <h1 className="font-display font-bold text-lg">{rec?.gameName ?? "Edit Post"}</h1>
            )}
          </div>
          <Button onClick={handleSave} disabled={updateRec.isPending || isLoading}>
            {updateRec.isPending ? "Saving…" : "Save"}
          </Button>
        </div>

        <div className="flex-1 overflow-hidden">
          {isLoading || !initialized ? (
            <div className="p-6">
              <Skeleton className="h-64 w-full" />
            </div>
          ) : (
            <TiptapEditor content={content} onChange={setContent} />
          )}
        </div>
      </div>
    </PageTransition>
  );
}
