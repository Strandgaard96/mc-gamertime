import {
  CalendarDays,
  Clock,
  Dices,
  ExternalLink,
  Gamepad2,
  Gauge,
  PenLine,
  Star,
  Trash2,
  Users2,
} from "lucide-react";
import { memo, useState } from "react";
import { Link } from "react-router-dom";
import { LogResultDialog } from "../components/LogResultDialog.tsx";
import { Dialog } from "../components/ui/dialog";
import { useAuth } from "../lib/AuthContext";
import { addGameFavorite, removeGameFavorite } from "../lib/api";
import type { Game } from "../lib/types";
import { cn, formatDate, idFromPk, pluralize, pressable } from "../lib/utils";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Tooltip } from "./ui/tooltip.tsx";

interface Props {
  game: Game;
  handleDelete?: (id: string) => void;
  playCounts?: number;
  lastPlayed?: string;
}

export const GameCard = memo(function GameCard({
  game,
  handleDelete,
  playCounts,
  lastPlayed,
}: Props) {
  const gameId = idFromPk(game.pk);
  const bggUrl = game.bggId ? `https://boardgamegeek.com/boardgame/${game.bggId}` : undefined;

  const [showDialog, setShowDialog] = useState(false);
  const [error, setError] = useState("");
  const [showLogDialog, setShowLogDialog] = useState(false);

  const { user } = useAuth();
  const [isFavorited, setIsFavorited] = useState(() => game.isFavorited ?? false);

  function closeDialog() {
    setShowDialog(false);
    setError("");
  }

  async function toggleFavorite(e: React.MouseEvent) {
    e.stopPropagation(); // prevent card link from firing

    try {
      if (isFavorited) {
        await removeGameFavorite(gameId);
        setIsFavorited(false);
      }
      if (!isFavorited) {
        await addGameFavorite(gameId);
        setIsFavorited(true);
      }
    } catch {
      setError("Failed to update favourite");
    }
  }

  const imageContent = game.imageUrl ? (
    <img src={game.imageUrl} alt={game.name} className="w-full h-40 object-contain bg-muted" />
  ) : (
    <div className="w-full h-40 bg-muted flex items-center justify-center text-muted-foreground">
      <Dices size={40} className="opacity-40" aria-hidden="true" />
    </div>
  );

  return (
    <div
      className={cn(
        "bg-card rounded-lg border hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all duration-200 group",
        pressable,
      )}
    >
      <div className="relative">
        <div className="relative">
          {user && (
            <button
              onClick={toggleFavorite}
              className={`absolute top-2 right-8 z-10 p-1.5 rounded-full bg-black/50 transition-colors ${
                isFavorited
                  ? "text-yellow-400 hover:bg-black/70"
                  : "text-white/70 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 hover:bg-black/70"
              }`}
            >
              <Star size={12} fill={isFavorited ? "currentColor" : "none"} />
            </button>
          )}
        </div>

        {playCounts && playCounts > 0 && (
          <Badge
            variant="secondary"
            className="absolute bottom-2 right-2 z-10 flex items-center gap-1.5 px-2 py-0.5 text-xs text-white bg-black/60 border-none backdrop-blur-xs cursor-help transition-transform hover:scale-105"
            title={lastPlayed ? `Last played ${formatDate(lastPlayed)}` : "Never played"}
          >
            <Gamepad2 size={12} className="opacity-80" />
            <span>Played {pluralize(playCounts, "time")}</span>
          </Badge>
        )}
        {bggUrl ? (
          <a href={bggUrl} target="_blank" rel="noopener noreferrer">
            {imageContent}
          </a>
        ) : (
          imageContent
        )}
        {game.imageUrl && (
          <div className="absolute inset-x-0 bottom-0 h-12 bg-linear-to-t from-card to-transparent pointer-events-none" />
        )}
        {handleDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowDialog(true);
            }}
            className="absolute top-2 left-2 z-10 p-1.5 rounded-full bg-black/50 text-white/70 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 hover:text-red-400 hover:bg-black/70 transition-all duration-200"
            title="Remove game"
          >
            <Trash2 size={12} />
          </button>
        )}

        {user?.role === "admin" ? (
          <Button
            variant="ghost"
            className="absolute top-2 right-2 z-10 p-1.5 rounded-full bg-black/50 text-white/70 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 hover:text-blue-300 hover:bg-black/70 transition-all duration-200"
            onClick={() => setShowLogDialog(true)}
          >
            <PenLine size={12} />
          </Button>
        ) : (
          <Tooltip text="Only admins can log results">
            <span>
              <Button
                variant="ghost"
                disabled
                className="absolute top-2 right-2 z-10 p-1.5 rounded-full bg-black/50 text-white/30 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 pointer-events-none transition-all duration-200"
              >
                <PenLine size={12} />
              </Button>
            </span>
          </Tooltip>
        )}
      </div>
      <div className="p-3">
        <Link
          to={`/games/${gameId}`}
          className="font-display font-semibold text-sm leading-tight mb-2 hover:text-primary transition-colors block"
        >
          {game.name}
        </Link>
        <div className="flex flex-wrap gap-x-3 gap-y-1 mb-2 text-xs text-muted-foreground">
          {game.minPlayers != null && game.maxPlayers != null && (
            <Badge variant="secondary" className="flex items-center gap-1 px-1.5 py-0 text-[10px]">
              <Users2 size={11} />
              {game.minPlayers}–{game.maxPlayers}
            </Badge>
          )}
          {game.playTime != null && (
            <span className="flex items-center gap-1">
              <Clock size={11} />
              {game.playTime}m
            </span>
          )}
          {game.weight != null && (
            <span className="flex items-center gap-1">
              <Gauge size={11} />
              {game.weight.toFixed(1)}
              <Tooltip text="Complexity rating (1-5). Higher means more rules and deeper strategy." />
            </span>
          )}
          {game.yearPublished != null && (
            <span className="flex items-center gap-1">
              <CalendarDays size={11} />
              {game.yearPublished}
            </span>
          )}
          {bggUrl && (
            <a
              href={bggUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-primary transition-colors mb-2"
            >
              <ExternalLink size={11} />
              BGG
            </a>
          )}
        </div>
        <Dialog open={showDialog} onClose={closeDialog} title="Delete Game">
          <div className="space-y-6">
            <div>
              <p className="text-xs text-muted-foreground">
                Are you sure you want to remove{" "}
                <span className="font-medium text-foreground">{game.name}</span> from your
                collection? This action cannot be undone.
              </p>
              {error && <p className="text-sm text-destructive mt-2">{error}</p>}
            </div>

            <div className="flex gap-3 justify-end">
              <Button type="button" variant="outline" onClick={closeDialog}>
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => {
                  if (handleDelete) handleDelete(gameId);
                  closeDialog();
                }}
              >
                Delete
              </Button>
            </div>
          </div>
        </Dialog>

        <LogResultDialog
          open={showLogDialog}
          onClose={() => setShowLogDialog(false)}
          defaultGameId={gameId}
        />
      </div>
    </div>
  );
});
