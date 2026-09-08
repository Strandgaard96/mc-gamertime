import { FileText, Plus } from "lucide-react";
import { Link } from "react-router-dom";
import { PageTransition } from "../components/PageTransition";
import { PostCard } from "../components/PostCard";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { usePosts } from "../hooks/usePosts";
import { useAuth } from "../lib/AuthContext";

export default function PostsPage() {
  const { data: posts = [], isLoading } = usePosts();
  const { user } = useAuth();
  const sorted = [...posts].sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  return (
    <PageTransition>
      <div className="max-w-2xl mx-auto p-4 md:p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-display font-bold flex items-center gap-2">
            <FileText size={24} className="text-primary" />
            Posts
          </h1>
          {user?.role === "admin" && (
            <Button asChild className="gap-1.5">
              <Link to="/posts/new">
                <Plus size={16} />
                New Post
              </Link>
            </Button>
          )}
        </div>
        {isLoading && (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-28 w-full" />
            ))}
          </div>
        )}
        {!isLoading && sorted.length === 0 && (
          <div className="text-center py-20 text-muted-foreground">
            <FileText size={48} className="mx-auto mb-4 opacity-30" />
            <p className="text-lg font-display font-semibold">No posts yet</p>
            {user?.role === "admin" && (
              <Button asChild className="mt-4 gap-1.5">
                <Link to="/posts/new">
                  <Plus size={16} />
                  Write the first post
                </Link>
              </Button>
            )}
          </div>
        )}
        <div className="space-y-3">
          {sorted.map((post) => (
            <PostCard key={post.pk} post={post} />
          ))}
        </div>
      </div>
    </PageTransition>
  );
}
