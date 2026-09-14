import * as React from "react";

import { GlowCard } from "@/components/ui/spotlight-card";
import { SectionTag } from "@/components/ui/section-tag";
import { OWNERS } from "@/data/site-data";

export function Owners() {
  return (
    <section id="owners" className="border-t border-line py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <SectionTag>Our Owners —</SectionTag>
        <h2 className="mt-4 font-serif text-3xl font-semibold text-white sm:text-4xl">
          The Visionaries Behind Bengal Tigers
        </h2>

        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {OWNERS.map((owner) => (
            <GlowCard key={owner.name} glowColor="red" tabIndex={0}>
              <div className="aspect-[4/5] w-full overflow-hidden bg-navy">
                <img
                  src={owner.image}
                  alt={owner.name}
                  className="h-full w-full object-cover object-top"
                />
              </div>
              <div className="border-t border-line bg-navy-panel p-6">
                <h3 className="font-serif text-xl font-semibold text-white">
                  {owner.name}
                </h3>
              </div>
            </GlowCard>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Owners;
