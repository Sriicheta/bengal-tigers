import * as React from "react";
import { ArrowRight } from "lucide-react";

import { SectionTag } from "@/components/ui/section-tag";
import { ClawWatermark } from "@/components/ui/claw-watermark";
import { PILLARS } from "@/data/site-data";

export function About() {
  return (
    <section id="about" className="relative overflow-hidden border-t border-line bg-navy py-24">
      <ClawWatermark className="pointer-events-none absolute -right-16 -top-16 h-[420px] w-[420px]" />

      <div className="relative mx-auto max-w-7xl px-5 md:px-8">
        <div className="grid gap-14 lg:grid-cols-2 lg:items-center">
          <div>
            <SectionTag>About the Franchise</SectionTag>
            <h2 className="mt-4 font-serif text-3xl font-semibold text-white sm:text-4xl">
              Carrying Bengal's Pride
            </h2>
            <p className="mt-6 text-base leading-relaxed text-mist sm:text-lg">
              Since taking the field, Bengal Tigers have carried the
              region's cricketing pride into the Celebrity Cricket League —
              a squad of performers who train like professionals and play
              like it matters, because to the fans back home, it does.
              Fearless batting, disciplined bowling, and a dressing room
              that never stops backing itself, over after over.
            </p>
            <a
              href="#roster"
              className="mt-8 inline-flex items-center gap-2 rounded-full bg-crimson px-7 py-3 text-sm font-semibold uppercase tracking-wide text-white transition-colors hover:bg-crimson-bright"
            >
              Read More
              <ArrowRight className="h-4 w-4" />
            </a>
          </div>

          <div className="grid gap-5">
            {PILLARS.map((p) => (
              <div
                key={p.title}
                className="flex items-start gap-5 rounded-2xl border border-line bg-navy-panel p-6"
              >
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-gold/40 text-gold-bright">
                  <p.icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="font-mono text-sm font-semibold uppercase tracking-[0.2em] text-gold-bright">
                    {p.title}
                  </p>
                  <p className="mt-2 text-sm leading-relaxed text-mist">
                    {p.copy}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

export default About;
