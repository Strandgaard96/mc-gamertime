import { X } from "lucide-react";
import { AnimatePresence, motion, type Variants } from "motion/react";
import { type ReactNode, useEffect, useState } from "react";
import { useCountUp } from "../hooks/useCountUp";

export interface WrappedSlide {
  key: string;
  icon: ReactNode;
  title: string;
  value: string | number;
  sub?: string;
}

interface WrappedOverlayProps {
  playerName: string;
  slides: WrappedSlide[];
  onClose: () => void;
}

const slideVariants: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1, transition: { duration: 0.25, ease: "easeOut" } },
  exit: { opacity: 0, scale: 0.95, transition: { duration: 0.15 } },
};

function SlideValue({ value }: { value: string | number }) {
  const count = useCountUp(typeof value === "number" ? value : 0);
  if (typeof value !== "number") {
    return <div className="text-3xl font-display font-bold text-center">{value}</div>;
  }
  return <div className="text-6xl font-display font-bold tabular-nums">{count}</div>;
}

export function WrappedOverlay({ playerName, slides, onClose }: WrappedOverlayProps) {
  const [index, setIndex] = useState(0);
  const isLast = index === slides.length - 1;

  const next = () => {
    if (isLast) onClose();
    else setIndex((i) => i + 1);
  };
  const prev = () => setIndex((i) => Math.max(0, i - 1));

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") next();
      else if (e.key === "ArrowLeft") prev();
      else if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose, prev, next]);

  const slide = slides[index];

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 bg-black/95 flex flex-col"
      aria-label={`${playerName}'s Wrapped`}
    >
      <div className="flex gap-1 px-3 pt-4 z-20">
        {slides.map((s, i) => (
          <div key={s.key} className="flex-1 h-1 rounded-full bg-white/20 overflow-hidden">
            <div
              className={`h-full bg-white transition-all duration-300 ${i <= index ? "w-full" : "w-0"}`}
            />
          </div>
        ))}
      </div>

      <button
        onClick={onClose}
        aria-label="Close"
        className="absolute top-4 right-3 z-20 text-white/70 hover:text-white p-1"
      >
        <X size={24} />
      </button>

      <div className="relative flex-1">
        <div className="absolute inset-0 z-10 flex" aria-hidden="true">
          <div className="w-1/3 h-full cursor-pointer" onClick={prev} />
          <div className="w-2/3 h-full cursor-pointer" onClick={next} />
        </div>

        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <AnimatePresence mode="wait">
            <motion.div
              key={slide.key}
              variants={slideVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              className="flex flex-col items-center gap-4 text-white px-8 text-center"
            >
              <div className="text-primary">{slide.icon}</div>
              {slide.value !== "" ? (
                <>
                  <SlideValue value={slide.value} />
                  <div className="text-lg font-medium text-white/90">{slide.title}</div>
                </>
              ) : (
                <div className="text-3xl font-display font-bold">{slide.title}</div>
              )}
              {slide.sub && <div className="text-sm text-white/60">{slide.sub}</div>}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
