import * as React from "react";
import { ChevronDown, ArrowRight } from "lucide-react";

import { KineticGrid } from "@/components/ui/kinetic-grid";
import { SectionTag } from "@/components/ui/section-tag";
import { CyclingWord } from "@/components/ui/cycling-word";
import { HEADLINE_WORDS, SEASON_RECORD, heroBatsman } from "@/data/site-data";

export function Hero() {
  return (
    <section className="relative flex min-h-[100svh] items-center overflow-hidden bg-obsidian">
      <img
        src={heroBatsman}
        alt="Bengal Tigers batsman silhouetted against stadium floodlights"
        className="absolute inset-0 h-full w-full object-cover opacity-90"
      />
      <div className="absolute inset-0 bg-gradient-to-r from-obsidian via-obsidian/55 to-obsidian/10" />
      <div className="absolute inset-0 bg-gradient-to-b from-obsidian/40 via-transparent to-obsidian" />
      <KineticGrid className="mix-blend-screen" spacing={38} warpStrength={14} />

      <div className="relative z-10 mx-auto w-full max-w-7xl px-5 pb-24 pt-32 md:px-8">
        <SectionTag>Welcome to the Pride of Bengal</SectionTag>

        <h1 className="mt-7 font-serif text-6xl font-bold uppercase leading-[0.95] tracking-tight sm:text-7xl md:text-8xl">
          <span className="block text-white">Bengal</span>
          <span className="block text-crimson-bright">Tigers</span>
        </h1>

        <p className="mt-6 max-w-xl font-serif text-2xl text-white/85 sm:text-3xl">
          Driven by <CyclingWord words={HEADLINE_WORDS} />
        </p>

        <p className="mt-6 max-w-lg text-base italic leading-relaxed text-mist sm:text-lg">
          Representing Bengal. Roaring for Glory.
        </p>

        <div className="mt-10 flex flex-wrap items-center gap-4">
          <a
            href="#roster"
            className="inline-flex items-center gap-2 rounded-full bg-crimson px-7 py-3.5 text-sm font-semibold uppercase tracking-wide text-white transition-colors hover:bg-crimson-bright"
          >
            Explore Team
            <ArrowRight className="h-4 w-4" />
          </a>
          <a
            href="#stats"
            className="rounded-full border border-white/20 bg-white/5 px-7 py-3.5 text-sm font-semibold uppercase tracking-wide text-white backdrop-blur-sm transition-colors hover:border-gold/50 hover:text-gold-bright"
          >
            Latest Matches
          </a>
        </div>

        <div className="mt-14 flex flex-wrap items-center gap-x-4 gap-y-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-white/50">
          {SEASON_RECORD.map((item, i) => (
            <React.Fragment key={item}>
              {i > 0 && <span className="text-gold">·</span>}
              <span>{item}</span>
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className="absolute bottom-8 left-1/2 z-10 -translate-x-1/2 text-white/40">
        <ChevronDown className="h-5 w-5 animate-bounce" />
      </div>
    </section>
  );
}

export default Hero;
