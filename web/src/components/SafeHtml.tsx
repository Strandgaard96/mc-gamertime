import DOMPurify from "dompurify";
import { useEffect, useRef } from "react";

interface Props {
  html: string;
  className?: string;
}

/** Renders sanitized HTML. Sanitizes with DOMPurify, inserts via DOMParser. */
export function SafeHtml({ html, className }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const clean = DOMPurify.sanitize(html);
    const doc = new DOMParser().parseFromString(clean, "text/html");
    ref.current.replaceChildren(...Array.from(doc.body.childNodes));
  }, [html]);

  return <div ref={ref} className={className} />;
}
