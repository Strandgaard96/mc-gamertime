import { useEffect, useState } from "react";

const COLORS = [
  "#e11d48",
  "#7c3aed",
  "#2563eb",
  "#0891b2",
  "#059669",
  "#d97706",
  "#c2410c",
  "#be185d",
];

interface Props {
  name: string;
  imageUrl?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}
export function Avatar({ name, imageUrl, size = "md", className = "" }: Props) {
  const [imgError, setImgError] = useState(false);

  // Reset error state when image URL changes
  useEffect(() => {
    setImgError(false);
  }, []);

  const color = COLORS[name.charCodeAt(0) % COLORS.length];
  const initials = name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const dim = { sm: "w-6 h-6 text-xs", md: "w-8 h-8 text-sm", lg: "w-12 h-12 text-base" }[size];

  if (imageUrl && !imgError) {
    return (
      <img
        src={imageUrl}
        alt={name}
        className={`${dim} rounded-full object-cover shrink-0 ${className}`}
        onError={() => setImgError(true)}
      />
    );
  }

  return (
    <div
      className={`${dim} rounded-full flex items-center justify-center font-semibold text-white shrink-0 ${className}`}
      style={{ backgroundColor: color }}
    >
      {initials}
    </div>
  );
}
