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
            <SectionTag>About Bengal Tigers</SectionTag>
            <h2 className="mt-4 font-serif text-3xl font-semibold text-white sm:text-4xl">
              Pride of Bengal. Passion for Cricket.
            </h2>
            <p className="mt-6 text-base leading-relaxed text-mist sm:text-lg">
              Bengal Tigers represent the spirit, culture and cinematic
              identity of Bengal on the Celebrity Cricket League stage.
              Since joining the CCL in 2012, the franchise has brought
              together some of Bengal's most popular actors and
              personalities, united by a shared passion for cricket. That
              journey delivered its defining moment in 2024, when Bengal
              Tigers won their first CCL championship — and continued in
              2026, defeating Kerala Strikers in the semi-final before
              finishing runners-up to Karnataka Bulldozers in a closely
              contested final. This is Bengal. This is our game. This is
              Bengal Tigers.
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
