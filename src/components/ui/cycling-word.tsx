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

  // The mask has no fixed height: it shrink-wraps the word, which inherits
  // the surrounding font-size/line-height. Since an overflow-hidden
  // inline-block aligns by its bottom edge, `align-bottom` pins that edge to
  // the line-box bottom — putting every word's baseline exactly on the
  // surrounding text's baseline. Travel is 100% of the word's own height so
  // it stays one full line at any text size.
  return (
    <span className="relative inline-block overflow-hidden align-bottom">
      <AnimatePresence mode="wait">
        <motion.span
          key={words[index]}
          initial={{ y: "100%", opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: "-100%", opacity: 0 }}
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
