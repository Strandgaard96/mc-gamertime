import { Layers, Plus } from "lucide-react";
import { useState } from "react";
import { AddGameDialog } from "../components/AddGameDialog";
import { GamePicker } from "../components/GamePicker";
import { PageTransition } from "../components/PageTransition";
import { Button } from "../components/ui/button";
import { useDeleteGame } from "../hooks/useGames";
import { useAuth } from "../lib/AuthContext";

export default function Catalog() {
  const deleteGame = useDeleteGame();
  const [showAdd, setShowAdd] = useState(false);
  const { user } = useAuth();

  return (
    <PageTransition>
      <div className="max-w-5xl mx-auto p-4 md:p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-display font-bold flex items-center gap-2">
            <Layers size={24} className="text-primary" />
            Game Catalog
          </h1>
          {user?.role === "admin" && (
            <Button onClick={() => setShowAdd(true)} className="gap-1.5">
              <Plus size={16} />
              Add Game
            </Button>
          )}
        </div>
        <GamePicker onDelete={user?.role === "admin" ? (id) => deleteGame.mutate(id) : undefined} />
        <AddGameDialog open={showAdd} onClose={() => setShowAdd(false)} />
      </div>
    </PageTransition>
  );
}
