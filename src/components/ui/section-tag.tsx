import * as React from "react";

export function SectionTag({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-gold/30 bg-gold/10 px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.25em] text-gold-bright">
      {children}
    </span>
  );
}

export default SectionTag;
