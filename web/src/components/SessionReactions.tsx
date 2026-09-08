import { SmilePlus, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";
import {
  useAddComment,
  useDeleteComment,
  useReactions,
  useToggleReaction,
} from "../hooks/useReactions";
import { useAuth } from "../lib/AuthContext";
import type { CommentItem, ReactionItem } from "../lib/types";
import { formatDate } from "../lib/utils";
import { Button } from "./ui/button";
import { Input } from "./ui/input";

const REACTION_EMOJIS = ["👍", "❤️", "😂", "😮", "🎉", "🔥"];

interface Props {
  sessionPk: string;
}

export function SessionReactions({ sessionPk }: Props) {
  const { user } = useAuth();
  const { data: items = [] } = useReactions();
  const toggleReaction = useToggleReaction();
  const addComment = useAddComment();
  const deleteComment = useDeleteComment();

  const [pickerOpen, setPickerOpen] = useState(false);
  const [commentsOpen, setCommentsOpen] = useState(false);
  const [text, setText] = useState("");

  const reactions = useMemo(
    () =>
      items.filter((i): i is ReactionItem => i.type === "reaction" && i.sessionPk === sessionPk),
    [items, sessionPk],
  );
  const comments = useMemo(
    () => items.filter((i): i is CommentItem => i.type === "comment" && i.sessionPk === sessionPk),
    [items, sessionPk],
  );

  const counts = useMemo(() => {
    const map = new Map<string, { count: number; mine: boolean }>();
    for (const r of reactions) {
      const entry = map.get(r.emoji) ?? { count: 0, mine: false };
      entry.count += 1;
      if (r.userId === user?.sub) entry.mine = true;
      map.set(r.emoji, entry);
    }
    return map;
  }, [reactions, user?.sub]);

  function handleToggle(emoji: string) {
    if (toggleReaction.isPending) return;
    toggleReaction.mutate({ sessionPk, emoji });
    setPickerOpen(false);
  }

  function handleAddComment() {
    const trimmed = text.trim();
    if (!trimmed) return;
    addComment.mutate({ sessionPk, text: trimmed }, { onSuccess: () => setText("") });
  }

  return (
    <div className="mt-1.5 space-y-1.5">
      <div className="flex items-center gap-1 flex-wrap relative">
        {[...counts.entries()].map(([emoji, { count, mine }]) => (
          <button
            key={emoji}
            onClick={() => handleToggle(emoji)}
            disabled={toggleReaction.isPending}
            className={`text-xs px-1.5 py-0.5 rounded-full border flex items-center gap-1 transition-colors ${
              mine
                ? "bg-primary/10 border-primary/40 text-primary"
                : "bg-card border-border text-muted-foreground hover:border-primary/20"
            }`}
          >
            <span>{emoji}</span>
            <span>{count}</span>
          </button>
        ))}
        <button
          onClick={() => setPickerOpen((o) => !o)}
          aria-label="Add reaction"
          className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-full hover:bg-muted/60"
        >
          <SmilePlus size={14} />
        </button>
        {pickerOpen && (
          <div
            role="menu"
            aria-label="Choose a reaction"
            className="absolute top-full left-0 mt-1 z-10 flex gap-1 p-1.5 rounded-lg bg-card border shadow-lg"
          >
            {REACTION_EMOJIS.map((emoji) => (
              <button
                key={emoji}
                onClick={() => handleToggle(emoji)}
                className="text-base hover:scale-125 transition-transform"
              >
                {emoji}
              </button>
            ))}
          </div>
        )}
      </div>

      <button
        type="button"
        onClick={() => setCommentsOpen((o) => !o)}
        aria-expanded={commentsOpen}
        className="inline-flex items-center gap-1 self-start rounded-md border px-2 py-1 text-xs text-muted-foreground hover:border-primary/40 hover:text-foreground transition-colors"
      >
        {comments.length > 0
          ? `💬 ${comments.length} comment${comments.length === 1 ? "" : "s"}`
          : "Add comment"}
      </button>

      {commentsOpen && (
        <div className="space-y-1.5 pl-2 border-l border-border">
          {comments.map((c) => (
            <div key={c.pk} className="text-xs flex items-start justify-between gap-2">
              <div>
                <span className="font-medium">{c.authorName}</span>{" "}
                <span className="text-muted-foreground">{formatDate(c.createdAt)}</span>
                <p>{c.text}</p>
              </div>
              {(user?.sub === c.authorId || user?.role === "admin") && (
                <button
                  onClick={() => deleteComment.mutate(c.pk)}
                  aria-label="Delete comment"
                  className="text-muted-foreground hover:text-destructive transition-colors p-0.5 shrink-0"
                >
                  <Trash2 size={12} />
                </button>
              )}
            </div>
          ))}
          <div className="flex items-center gap-1.5">
            <Input
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Add a comment..."
              maxLength={500}
              className="h-7 text-xs"
              onKeyDown={(e) => {
                if (e.key === "Enter") handleAddComment();
              }}
            />
            <Button
              size="sm"
              onClick={handleAddComment}
              disabled={addComment.isPending || !text.trim()}
            >
              Send
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
