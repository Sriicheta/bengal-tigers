import * as React from "react";

import { PlayerCarousel } from "@/components/ui/player-carousel";
import { SectionTag } from "@/components/ui/section-tag";
import { ROSTER } from "@/data/site-data";

export function Roster() {
  return (
    <section id="roster" className="border-t border-line py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <SectionTag>The Roster —</SectionTag>
        <h2 className="mt-4 font-serif text-3xl font-semibold text-white sm:text-4xl">
          The Squad
        </h2>
        <p className="mt-4 max-w-xl text-sm text-mist">
          Drag or use the arrows to browse the roster. Confirmed playing
          stats land with the next squad update.
        </p>

        <div className="mt-12">
          <PlayerCarousel players={ROSTER} />
        </div>
      </div>
    </section>
  );
}

export default Roster;
