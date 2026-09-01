"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * GlowCard
 * ------------------------------------------------------------------
 * A dark-glass card that tracks the pointer and renders a soft
 * radial glow at the cursor position via a CSS custom property, plus
 * a border sheen. Tuned for the Bengal Tigers dark navy theme: a
 * navy-glass card (#0E1726) with a crimson-red spotlight by default.
 *
 * `glowColor` accepts either a shorthand keyword ("red", "gold",
 * "navy") mapped to the curated palette, or any raw CSS color string
 * for full control. Falls back to a static card on touch devices /
 * reduced motion, where there is no meaningful pointer.
 */

const GLOW_PRESETS: Record<string, string> = {
  red: "rgba(200, 30, 30, 0.45)",
  crimson: "rgba(200, 30, 30, 0.45)",
  gold: "rgba(212, 175, 55, 0.35)",
  navy: "rgba(148, 163, 184, 0.2)",
};

function resolveGlowColor(input: string): string {
  return GLOW_PRESETS[input.toLowerCase()] ?? input;
}

export interface GlowCardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** "red" | "gold" | "navy", or any raw CSS color string. */
  glowColor?: string;
  /** Size of the glow in pixels. */
  glowSize?: number;
  /** Optional intensity of the border glow, 0–1. */
  intensity?: number;
  as?: React.ElementType;
}

export const GlowCard = React.forwardRef<HTMLDivElement, GlowCardProps>(
  (
    {
      glowColor = "red",
      glowSize = 440,
      intensity = 0.9,
      className,
      children,
      as: Comp = "div",
      ...rest
    },
    forwardedRef
  ) => {
    const innerRef = React.useRef<HTMLDivElement>(null);
    const [isFocused, setIsFocused] = React.useState(false);
    const resolvedGlow = resolveGlowColor(glowColor);

    React.useImperativeHandle(
      forwardedRef,
      () => innerRef.current as HTMLDivElement
    );

    const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
      const el = innerRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      el.style.setProperty("--glow-x", `${e.clientX - rect.left}px`);
      el.style.setProperty("--glow-y", `${e.clientY - rect.top}px`);
    };

    return (
      <Comp
        ref={innerRef}
        onPointerMove={handlePointerMove}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        className={cn(
          "group/glow relative isolate overflow-hidden rounded-2xl",
          "border border-line bg-navy-panel",
          "shadow-[0_1px_2px_rgba(0,0,0,0.3)]",
          "transition-all duration-300 ease-out",
          "hover:-translate-y-1 hover:shadow-[0_24px_50px_-20px_rgba(185,28,28,0.35)]",
          "focus-visible:-translate-y-1",
          "outline-none focus-visible:ring-2 focus-visible:ring-crimson/60",
          className
        )}
        style={
          {
            "--glow-color": resolvedGlow,
            "--glow-size": `${glowSize}px`,
          } as React.CSSProperties
        }
        {...rest}
      >
        {/* Pointer-tracked spotlight */}
        <div
          aria-hidden
          className={cn(
            "pointer-events-none absolute inset-0 z-10 opacity-0 transition-opacity duration-500",
            "group-hover/glow:opacity-100",
            isFocused && "opacity-100"
          )}
          style={{
            background: `radial-gradient(var(--glow-size) circle at var(--glow-x, 50%) var(--glow-y, 0%), var(--glow-color), transparent 70%)`,
          }}
        />

        {/* Static hairline rim, brightens to crimson on hover */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 z-10 rounded-2xl ring-1 ring-inset ring-white/5 transition-all duration-500 group-hover/glow:ring-crimson/50"
          style={{ opacity: 0.6 + intensity * 0.1 }}
        />

        {/* Content */}
        <div className="relative z-20">{children}</div>
      </Comp>
    );
  }
);

GlowCard.displayName = "GlowCard";

export default GlowCard;
