import Image from "@tiptap/extension-image";
import Link from "@tiptap/extension-link";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { useRef, useState } from "react";
import { toast } from "sonner";
import { getUploadUrl } from "../lib/api";
import { Button } from "./ui/button";

const EMOJI = [
  "😀",
  "😄",
  "😂",
  "🥳",
  "😎",
  "🤔",
  "😱",
  "🤩",
  "🎲",
  "🃏",
  "♟️",
  "🧩",
  "🏆",
  "🥇",
  "🔥",
  "⚡",
  "🍕",
  "🍺",
  "☕",
  "🍿",
  "🎉",
  "👏",
  "💀",
  "❤️",
];

interface Props {
  content: string;
  onChange: (html: string) => void;
}

export function TiptapEditor({ content, onChange }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [emojiOpen, setEmojiOpen] = useState(false);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Image.configure({ inline: false }),
      Link.configure({ openOnClick: false }),
    ],
    content,
    onUpdate: ({ editor }) => onChange(editor.getHTML()),
  });

  if (!editor) return null;

  async function handleImageUpload(file: File) {
    try {
      const { uploadUrl, imageUrl } = await getUploadUrl(file.name, file.type);
      await fetch(uploadUrl, { method: "PUT", body: file, headers: { "Content-Type": file.type } });
      editor?.chain().focus().setImage({ src: imageUrl }).run();
    } catch (e) {
      console.error("Image upload failed", e);
      toast.error("Image upload failed");
    }
  }

  function toolbarBtn(active: boolean, onClick: () => void, label: string) {
    return (
      <Button
        key={label}
        type="button"
        variant={active ? "default" : "ghost"}
        size="sm"
        onClick={onClick}
        className="h-7 px-2 text-xs"
      >
        {label}
      </Button>
    );
  }

  return (
    <div className="rounded-lg border border-input overflow-hidden">
      <div className="flex flex-wrap gap-1 p-2 border-b bg-muted/40">
        {toolbarBtn(editor.isActive("bold"), () => editor.chain().focus().toggleBold().run(), "B")}
        {toolbarBtn(
          editor.isActive("italic"),
          () => editor.chain().focus().toggleItalic().run(),
          "I",
        )}
        {toolbarBtn(
          editor.isActive("heading", { level: 2 }),
          () => editor.chain().focus().toggleHeading({ level: 2 }).run(),
          "H2",
        )}
        {toolbarBtn(
          editor.isActive("heading", { level: 3 }),
          () => editor.chain().focus().toggleHeading({ level: 3 }).run(),
          "H3",
        )}
        {toolbarBtn(
          editor.isActive("bulletList"),
          () => editor.chain().focus().toggleBulletList().run(),
          "• List",
        )}
        {toolbarBtn(
          editor.isActive("orderedList"),
          () => editor.chain().focus().toggleOrderedList().run(),
          "1. List",
        )}
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="h-7 px-2 text-xs"
          onClick={() => {
            const url = window.prompt("Enter URL");
            if (url) editor.chain().focus().setLink({ href: url }).run();
          }}
        >
          Link
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="h-7 px-2 text-xs"
          onClick={() => fileInputRef.current?.click()}
        >
          Image
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleImageUpload(f);
            e.target.value = "";
          }}
        />
        <div className="relative">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-7 px-2 text-xs"
            onClick={() => setEmojiOpen((o) => !o)}
          >
            😊
          </Button>
          {emojiOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setEmojiOpen(false)} />
              <div className="absolute left-0 top-8 z-20 grid w-72 grid-cols-8 gap-1 rounded-lg border bg-card p-2 shadow-md">
                {EMOJI.map((e) => (
                  <button
                    key={e}
                    type="button"
                    className="text-lg p-1 rounded hover:bg-accent transition-colors"
                    onClick={() => {
                      editor.chain().focus().insertContent(e).run();
                      setEmojiOpen(false);
                    }}
                  >
                    {e}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
      <EditorContent
        editor={editor}
        className="prose prose-sm dark:prose-invert max-w-none p-4 min-h-48 focus-within:outline-none"
      />
    </div>
  );
}
