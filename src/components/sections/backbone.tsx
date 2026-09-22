import * as React from "react";

import { GlowCard } from "@/components/ui/spotlight-card";
import { SectionTag } from "@/components/ui/section-tag";
import { BACKBONE_MEMBERS, type BackboneMember } from "@/data/site-data";

function initials(name: string) {
  const clean = name.replace(/\(.*?\)/g, "").trim();
  const parts = clean.split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function BackboneCard({ member }: { member: BackboneMember }) {
  return (
    <GlowCard glowColor="red" tabIndex={0}>
      {member.image ? (
        <div className="aspect-[4/5] w-full overflow-hidden bg-navy">
          <img
            src={member.image}
            alt={member.name}
            className="block h-full w-full object-cover object-top"
            style={{
              objectPosition: member.imagePosition,
              transform:
                member.imageScale && member.imageScale !== 1
                  ? `scale(${member.imageScale})`
                  : undefined,
              transformOrigin: member.imageOrigin ?? member.imagePosition,
            }}
            loading="lazy"
          />
        </div>
      ) : (
        <div
          aria-label={`${member.name} photo coming soon`}
          role="img"
          className="flex aspect-[4/5] w-full flex-col items-center justify-center gap-4 bg-gradient-to-b from-navy-panel to-navy px-6 text-center"
        >
          <span className="flex h-20 w-20 items-center justify-center rounded-full border border-gold/30 bg-gold/10 font-serif text-3xl font-semibold text-gold-bright">
            {initials(member.name)}
          </span>
          <span className="font-mono text-[10px] uppercase tracking-[0.25em] text-mist">
            Photo coming soon
          </span>
        </div>
      )}
      <div className="border-t border-line bg-navy-panel p-6 text-center">
        <h3 className="font-serif text-xl font-semibold text-white">
          {member.name}
        </h3>
        <span className="mt-3 inline-flex items-center rounded-full border border-gold/40 bg-black/60 px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-gold">
          {member.designation}
        </span>
      </div>
    </GlowCard>
  );
}

export function Backbone() {
  return (
    <section id="backbone" className="border-t border-line bg-navy py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <SectionTag>Backbone —</SectionTag>
        <h2 className="mt-4 font-serif text-3xl font-semibold text-white sm:text-4xl">
          The Backbone of Bengal Tigers
        </h2>

        <div className="mt-14 grid items-stretch gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {BACKBONE_MEMBERS.map((member) => (
            <BackboneCard key={member.id} member={member} />
          ))}
        </div>
      </div>
    </section>
  );
}

export default Backbone;
