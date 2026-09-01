"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * KineticGrid
 * ------------------------------------------------------------------
 * A full-bleed canvas of dots arranged in a grid. Each dot is pulled
 * toward the pointer (a "warp") and pushed outward in a radial pulse
 * whenever the surface is clicked or tapped (a "ripple"). Built for
 * use as a hero background — pointer events pass through to any
 * interactive content layered on top unless `interactive` is true.
 *
 * Respects prefers-reduced-motion by rendering a still grid.
 */

type Ripple = {
  x: number;
  y: number;
  born: number;
};

export interface KineticGridProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Spacing between grid dots in pixels. */
  spacing?: number;
  /** Base radius of each dot in pixels. */
  dotRadius?: number;
  /** How far the pointer field reaches, in pixels. */
  warpRadius?: number;
  /** How strongly dots are displaced toward the pointer, in pixels. */
  warpStrength?: number;
  /** Primary dot color (CSS color string). */
  color?: string;
  /** Brighter color used near the pointer / inside ripples. */
  accentColor?: string;
  /** Whether the canvas itself should capture pointer events (true) or
   *  let them fall through to content behind/above it (false, default). */
  interactive?: boolean;
  className?: string;
}

export const KineticGrid: React.FC<KineticGridProps> = ({
  spacing = 34,
  dotRadius = 1.3,
  warpRadius = 190,
  warpStrength = 16,
  color = "rgba(148, 163, 184, 0.14)",
  accentColor = "rgba(226, 232, 240, 0.65)",
  interactive = false,
  className,
  ...rest
}) => {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const pointer = React.useRef({ x: -9999, y: -9999, active: false });
  const ripples = React.useRef<Ripple[]>([]);
  const rafRef = React.useRef<number | undefined>(undefined);
  const dimsRef = React.useRef({ w: 0, h: 0, dpr: 1 });

  React.useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    const resize = () => {
      const rect = container.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.floor(rect.width * dpr);
      canvas.height = Math.floor(rect.height * dpr);
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
      dimsRef.current = { w: rect.width, h: rect.height, dpr };
    };

    resize();
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(container);

    const handlePointerMove = (e: PointerEvent) => {
      const rect = container.getBoundingClientRect();
      pointer.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
        active: true,
      };
    };
    const handlePointerLeave = () => {
      pointer.current.active = false;
    };
    const handlePointerDown = (e: PointerEvent) => {
      const rect = container.getBoundingClientRect();
      ripples.current.push({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
        born: performance.now(),
      });
      if (ripples.current.length > 4) ripples.current.shift();
    };

    container.addEventListener("pointermove", handlePointerMove);
    container.addEventListener("pointerleave", handlePointerLeave);
    container.addEventListener("pointerdown", handlePointerDown);

    const draw = () => {
      const { w, h, dpr } = dimsRef.current;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);

      const now = performance.now();
      const { x: px, y: py, active } = pointer.current;

      const cols = Math.ceil(w / spacing) + 1;
      const rows = Math.ceil(h / spacing) + 1;

      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          const gx = i * spacing;
          const gy = j * spacing;

          let dx = 0;
          let dy = 0;
          let glow = 0;

          if (active && !prefersReducedMotion) {
            const distX = gx - px;
            const distY = gy - py;
            const dist = Math.sqrt(distX * distX + distY * distY);
            if (dist < warpRadius) {
              const force = (1 - dist / warpRadius) ** 2;
              const angle = Math.atan2(distY, distX);
              dx = Math.cos(angle) * force * warpStrength;
              dy = Math.sin(angle) * force * warpStrength;
              glow = force;
            }
          }

          if (!prefersReducedMotion) {
            for (const r of ripples.current) {
              const age = now - r.born;
              const life = 1400;
              if (age > life) continue;
              const t = age / life;
              const ringRadius = t * 420;
              const distX = gx - r.x;
              const distY = gy - r.y;
              const dist = Math.sqrt(distX * distX + distY * distY);
              const band = Math.abs(dist - ringRadius);
              if (band < 40) {
                const force = (1 - band / 40) * (1 - t);
                const angle = Math.atan2(distY, distX);
                dx += Math.cos(angle) * force * 10;
                dy += Math.sin(angle) * force * 10;
                glow = Math.max(glow, force);
              }
            }
          }

          const r = dotRadius + glow * 1.6;
          ctx.beginPath();
          ctx.fillStyle = glow > 0.08 ? accentColor : color;
          ctx.arc(gx + dx, gy + dy, r, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      ripples.current = ripples.current.filter(
        (r) => now - r.born < 1400
      );

      rafRef.current = requestAnimationFrame(draw);
    };

    rafRef.current = requestAnimationFrame(draw);

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      resizeObserver.disconnect();
      container.removeEventListener("pointermove", handlePointerMove);
      container.removeEventListener("pointerleave", handlePointerLeave);
      container.removeEventListener("pointerdown", handlePointerDown);
    };
  }, [spacing, dotRadius, warpRadius, warpStrength, color, accentColor]);

  return (
    <div
      ref={containerRef}
      className={cn("absolute inset-0 h-full w-full", className)}
      style={{ pointerEvents: interactive ? "auto" : "none" }}
      {...rest}
    >
      <canvas ref={canvasRef} className="block h-full w-full" />
    </div>
  );
};

export default KineticGrid;
