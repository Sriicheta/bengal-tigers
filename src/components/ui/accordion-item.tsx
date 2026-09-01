"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";

export interface AccordionItemProps {
  q: string;
  a: string;
  open: boolean;
  onToggle: () => void;
}

export function AccordionItem({ q, a, open, onToggle }: AccordionItemProps) {
  return (
    <div className="border-b border-line">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-4 py-5 text-left"
        aria-expanded={open}
      >
        <span className="font-serif text-lg text-white">{q}</span>
        <ChevronDown
          className={`h-5 w-5 shrink-0 text-gold transition-transform duration-300 ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>
      <motion.div
        initial={false}
        animate={{ height: open ? "auto" : 0, opacity: open ? 1 : 0 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="overflow-hidden"
      >
        <p className="pb-5 pr-8 text-sm leading-relaxed text-mist">{a}</p>
      </motion.div>
    </div>
  );
}

export default AccordionItem;
