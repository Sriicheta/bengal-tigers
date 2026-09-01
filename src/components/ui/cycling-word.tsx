"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";

export function CyclingWord({ words }: { words: string[] }) {
  const [index, setIndex] = React.useState(0);

  React.useEffect(() => {
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;
    if (prefersReducedMotion) return;
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % words.length);
    }, 2200);
    return () => clearInterval(id);
  }, [words.length]);

  return (
    <span className="relative inline-block h-[1.15em] overflow-hidden align-bottom">
      <AnimatePresence mode="wait">
        <motion.span
          key={words[index]}
          initial={{ y: 26, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -26, opacity: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="inline-block text-crimson-bright"
        >
          {words[index]}
        </motion.span>
      </AnimatePresence>
    </span>
  );
}

export default CyclingWord;
