export interface PostDraft {
  title: string;
  content: string;
  sessionPk: string;
  savedAt: string; // ISO
}

export function useDraft(key: string) {
  function load(): PostDraft | null {
    try {
      const raw = localStorage.getItem(key);
      return raw ? (JSON.parse(raw) as PostDraft) : null;
    } catch {
      return null;
    }
  }

  function save(draft: Omit<PostDraft, "savedAt">) {
    try {
      localStorage.setItem(key, JSON.stringify({ ...draft, savedAt: new Date().toISOString() }));
    } catch {
      // storage quota exceeded — silently swallow
    }
  }

  function clear() {
    localStorage.removeItem(key);
  }

  return { load, save, clear };
}
