import * as React from "react";

import { SectionTag } from "@/components/ui/section-tag";
import { HEAD_COACH } from "@/data/site-data";

export function HeadCoach() {
  return (
    <section id="head-coach" className="border-t border-line bg-navy py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <SectionTag>Leadership —</SectionTag>
        <h2 className="mt-4 font-serif text-3xl font-semibold text-white sm:text-4xl">
          The Head Coach
        </h2>

        <div className="mt-12 grid gap-0 overflow-hidden rounded-3xl border border-gold/40 bg-navy-panel shadow-[0_30px_60px_-25px_rgba(212,175,55,0.15)] sm:grid-cols-[260px_1fr]">
          <div className="relative h-72 sm:h-full">
            <img
              src={HEAD_COACH.image}
              alt={HEAD_COACH.name}
              className="h-full w-full object-cover object-top"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-navy-panel/70 via-transparent to-transparent sm:bg-gradient-to-r" />
          </div>
          <div className="flex flex-col justify-center p-8 sm:p-10">
            <span className="inline-flex w-fit items-center gap-1.5 rounded-full border border-gold/40 bg-gold/15 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.2em] text-gold-bright">
              Head Coach
            </span>
            <h3 className="mt-4 font-serif text-3xl font-semibold text-white sm:text-4xl">
              {HEAD_COACH.name}
            </h3>
            <p className="mt-4 max-w-md text-sm leading-relaxed text-mist">
              Leads the Bengal Tigers dugout — setting matchday strategy,
              shaping the squad's preparation, and calling the final XI
              alongside team management.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default HeadCoach;
