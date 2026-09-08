import { useEffect, useState } from "react";

export function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);

    return () => clearTimeout(timer);
    // YOUR CODE:
    // 1. Start a timer: const timer = setTimeout(() => setDebounced(value), delay)
    // 2. Return a cleanup function: return () => clearTimeout(timer)
    //
    // How it works: every time `value` changes, React runs this effect.
    // The cleanup cancels the previous timer before starting a new one.
    // So if the user types fast, only the LAST keystroke's timer ever fires.
  }, [value, delay]);

  return debounced;
}
