"use client";

import * as React from "react";
import { useInView } from "framer-motion";

export interface AnimatedStatProps {
  icon: React.ElementType;
  label: string;
  value: string;
}

export function AnimatedStat({ icon: Icon, label, value }: AnimatedStatProps) {
  const ref = React.useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const numeric = parseFloat(value.replace(/[^0-9.]/g, "")) || 0;
  const suffix = value.replace(/[0-9.]/g, "");
  const [display, setDisplay] = React.useState(0);

  React.useEffect(() => {
    if (!inView) return;
    const duration = 1200;
    const start = performance.now();
    let raf: number;
    const tick = (now: number) => {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(numeric * eased);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [inView, numeric]);

  return (
    <div ref={ref} className="text-center">
      <Icon className="mx-auto h-6 w-6 text-gold-bright" />
      <p className="mt-4 font-serif text-4xl font-semibold text-white sm:text-5xl">
        {Math.round(display)}
        <span>{suffix}</span>
      </p>
      <p className="mt-2 font-mono text-[11px] uppercase tracking-[0.2em] text-white/70">
        {label}
      </p>
    </div>
  );
}

export default AnimatedStat;
