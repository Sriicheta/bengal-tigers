"use client";

import * as React from "react";
import { motion, useMotionValue, animate } from "framer-motion";
import { ChevronLeft, ChevronRight, Star } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * PlayerCarousel
 * ------------------------------------------------------------------
 * A linear, draggable horizontal carousel for the roster. Each card
 * shows the player photo, name, role badge, jersey number and a
 * headline stat. Built on Framer Motion drag (no external carousel
 * dependency required) with arrow-button and keyboard navigation.
 * Styled for the dark navy / crimson / gold theme — navy-glass
 * cards, crimson jersey numbers, gold role badges. The Head Coach
 * card sits at the end of the same carousel, marked out with a gold
 * border and a "Head Coach" ribbon.
 */

export type PlayerRole =
  | "Captain"
  | "Wicket-Keeper"
  | "All-Rounder"
  | "Batter"
  | "Bowler"
  | "Head Coach";

/** RHB = Right-Hand Batsman, LHB = Left-Hand Batsman */
export type BattingStyle = "RHB" | "LHB";

/** RAM = Right-Arm Medium, RAO = Right-Arm Off-break, RAL = Right-Arm Leg-break,
 *  LAM = Left-Arm Medium, LAO = Left-Arm Orthodox, LAL = Left-Arm Chinaman */
export type BowlingStyle = "RAM" | "RAO" | "RAL" | "LAM" | "LAO" | "LAL";

export interface Player {
  id: string;
  name: string;
  role?: PlayerRole;
  battingStyle?: BattingStyle;
  bowlingStyle?: BowlingStyle;
  jerseyNumber: number;
  /** Import path / URL for the player photo. */
  image: string;
  /** e.g. "1,204 runs · SR 148" or, for bowlers, "62 wkts · Econ 6.8" */
  primaryStat?: string;
  secondaryStat?: string;
  isCoach?: boolean;
  /**
   * Optional per-photo framing inside the fixed card image frame
   * (CSS only — the source file is never altered). `imagePosition`
   * aligns the cover-fit crop, `imageScale` applies a uniform
   * (non-distorting) zoom, `imageOrigin` anchors that zoom on the
   * subject so the head stays centered. Unset = default framing.
   */
  imagePosition?: string;
  imageScale?: number;
  imageOrigin?: string;
}

export interface PlayerCarouselProps {
  players: Player[];
  className?: string;
}

const CARD_WIDTH = 268;
const CARD_GAP = 20;

export const PlayerCarousel: React.FC<PlayerCarouselProps> = ({
  players,
  className,
}) => {
  const trackRef = React.useRef<HTMLDivElement>(null);
  const viewportRef = React.useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const [dragConstraint, setDragConstraint] = React.useState(0);
  const [activeIndex, setActiveIndex] = React.useState(0);

  const step = CARD_WIDTH + CARD_GAP;

  React.useEffect(() => {
    const calc = () => {
      const viewport = viewportRef.current;
      if (!viewport) return;
      const trackWidth = players.length * step - CARD_GAP;
      const max = Math.max(trackWidth - viewport.clientWidth, 0);
      setDragConstraint(-max);
    };
    calc();
    window.addEventListener("resize", calc);
    return () => window.removeEventListener("resize", calc);
  }, [players.length, step]);

  const goTo = (index: number) => {
    const clamped = Math.max(0, Math.min(index, players.length - 1));
    setActiveIndex(clamped);
    const viewport = viewportRef.current;
    const visibleCards = viewport
      ? Math.max(1, Math.floor(viewport.clientWidth / step))
      : 1;
    const maxStart = Math.max(players.length - visibleCards, 0);
    const target = -Math.min(clamped, maxStart) * step;
    const bounded = Math.max(target, dragConstraint);
    animate(x, bounded, { type: "spring", stiffness: 260, damping: 32 });
  };

  return (
    <div className={cn("relative", className)}>
      <div ref={viewportRef} className="overflow-hidden">
        <motion.div
          ref={trackRef}
          className="flex cursor-grab gap-5 active:cursor-grabbing"
          style={{ x }}
          drag="x"
          dragConstraints={{ left: dragConstraint, right: 0 }}
          dragElastic={0.06}
          whileTap={{ cursor: "grabbing" }}
        >
          {players.map((player, i) => (
            <PlayerCard key={player.id} player={player} index={i} />
          ))}
        </motion.div>
      </div>

      {/* Controls */}
      <div className="mt-8 flex items-center justify-between">
        <div className="flex gap-1.5">
          {players.map((p, i) => (
            <button
              key={p.id}
              aria-label={`Go to ${p.name}`}
              onClick={() => goTo(i)}
              className={cn(
                "h-1 rounded-full transition-all duration-300",
                activeIndex === i
                  ? "w-6 bg-crimson"
                  : "w-1.5 bg-white/15 hover:bg-white/30"
              )}
            />
          ))}
        </div>
        <div className="flex gap-2">
          <button
            aria-label="Previous player"
            onClick={() => goTo(activeIndex - 1)}
            className="flex h-10 w-10 items-center justify-center rounded-full border border-line bg-navy-panel text-white transition-colors hover:border-crimson/50 hover:bg-crimson/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-crimson/50"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            aria-label="Next player"
            onClick={() => goTo(activeIndex + 1)}
            className="flex h-10 w-10 items-center justify-center rounded-full border border-line bg-navy-panel text-white transition-colors hover:border-crimson/50 hover:bg-crimson/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-crimson/50"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

const PlayerCard: React.FC<{ player: Player; index: number }> = ({
  player,
}) => {
  return (
    <div
      className={cn(
        "group relative shrink-0 select-none overflow-hidden rounded-2xl border bg-navy-panel shadow-[0_1px_2px_rgba(0,0,0,0.35)] transition-shadow duration-300 hover:shadow-[0_20px_45px_-20px_rgba(0,0,0,0.6)]",
        player.isCoach ? "border-gold/50" : "border-line"
      )}
      style={{ width: CARD_WIDTH }}
    >
      {/* Jersey number, scoreboard-style */}
      <div className="absolute left-3 top-3 z-20 flex h-9 min-w-9 items-center justify-center rounded-md border border-crimson/50 bg-black/50 px-1.5 font-mono text-sm font-semibold text-white backdrop-blur-sm">
        {player.isCoach ? "HC" : String(player.jerseyNumber).padStart(2, "0")}
      </div>

      {player.isCoach && (
        <div className="absolute right-3 top-3 z-20 flex items-center gap-1 rounded-full border border-gold/50 bg-gold/15 px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-gold-bright">
          <Star className="h-3 w-3 fill-current" />
          Head Coach
        </div>
      )}

      <div className="relative h-72 w-full overflow-hidden bg-navy">
        <img
          src={player.image}
          alt={player.name}
          draggable={false}
          className="h-full w-full object-cover object-top"
          style={{
            objectPosition: player.imagePosition,
            transform:
              player.imageScale && player.imageScale !== 1
                ? `scale(${player.imageScale})`
                : undefined,
            transformOrigin: player.imageOrigin ?? player.imagePosition,
          }}
        />
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-navy-panel via-navy-panel/10 to-transparent" />
      </div>

      <div className="relative z-10 -mt-10 px-4 pb-5">
        {player.role && !player.isCoach && (
          <span className="inline-flex origin-left items-center rounded-full border border-gold/40 bg-black/60 px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-gold shadow-sm backdrop-blur-sm transition-all duration-300 group-hover:scale-[1.06] group-hover:border-gold-bright/80 group-hover:bg-black/80 group-hover:text-gold-bright group-hover:shadow-[0_0_16px_-2px_rgba(229,193,88,0.6)]">
            {player.role}
          </span>
        )}
        <h3 className="mt-2 truncate font-serif text-lg font-semibold text-white">
          {player.name}
        </h3>
        {(player.battingStyle || player.bowlingStyle) && (
          <p className="mt-1 font-mono text-[11px] tracking-wide text-mist">
            {[player.battingStyle, player.bowlingStyle].filter(Boolean).join(" · ")}
          </p>
        )}
        {(player.primaryStat || player.secondaryStat) && (
          <div className="mt-3 space-y-1 border-t border-line pt-3">
            {player.primaryStat && (
              <p className="font-mono text-xs text-white/90">
                {player.primaryStat}
              </p>
            )}
            {player.secondaryStat && (
              <p className="font-mono text-[11px] text-mist">
                {player.secondaryStat}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayerCarousel;
