import * as React from "react";

import { AnimatedStat } from "@/components/ui/animated-stat";
import { SectionTag } from "@/components/ui/section-tag";
import { STATS } from "@/data/site-data";

export function Stats() {
  return (
    <section id="stats" className="border-t border-line bg-crimson-deep py-20">
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="text-center">
          <SectionTag>Our Journey So Far</SectionTag>
        </div>
        <div className="mt-14 grid grid-cols-2 gap-10 sm:grid-cols-4">
          {STATS.map((s) => (
            <AnimatedStat key={s.label} {...s} />
          ))}
        </div>
      </div>
    </section>
  );
}

export default Stats;
