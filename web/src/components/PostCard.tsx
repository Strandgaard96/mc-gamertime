import { Link } from "react-router-dom";
import type { Post } from "../lib/types";
import { cn, excerpt, formatDate, idFromPk, pressable } from "../lib/utils";
import { Badge } from "./ui/badge";

interface Props {
  post: Post;
}

export function PostCard({ post }: Props) {
  const postId = idFromPk(post.pk);
  const gameId = post.gamePk ? idFromPk(post.gamePk) : null;
  return (
    <div
      className={cn(
        "bg-card rounded-lg border p-4 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 hover:-translate-y-0.5 transition-all duration-200 space-y-2",
        pressable,
      )}
    >
      <Link
        to={`/posts/${postId}`}
        className="font-display font-semibold hover:text-primary transition-colors block"
      >
        {post.title}
      </Link>
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        {gameId && post.gameName ? (
          <Link to={`/games/${gameId}`}>
            <Badge variant="secondary" className="cursor-pointer hover:bg-secondary/80">
              {post.gameName}
            </Badge>
          </Link>
        ) : null}
        <span>{formatDate(post.createdAt)}</span>
      </div>
      <p className="text-sm text-muted-foreground">{excerpt(post.content)}</p>
    </div>
  );
}
