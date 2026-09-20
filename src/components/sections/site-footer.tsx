import * as React from "react";
import { MapPin, Phone, Facebook, Instagram, Linkedin } from "lucide-react";

import { CONTACT, NAV_FOOTER_LINKS, bengalTigersLogo } from "@/data/site-data";

export function SiteFooter() {
  return (
    <footer id="footer" className="border-t border-line bg-navy py-16">
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="grid gap-10 md:grid-cols-[1.2fr_1fr_1fr]">
          <div>
            <div className="flex items-center gap-2.5">
              <img src={bengalTigersLogo} alt="Bengal Tigers crest" className="h-10 w-auto" />
              <span className="font-serif text-lg font-semibold text-white">
                BENGAL TIGERS
              </span>
            </div>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-mist">
              Representing Bengal. Roaring for Glory. Official home of
              Bengal Tigers, Celebrity Cricket League.
            </p>
          </div>

          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-gold-bright">
              Quick Links
            </p>
            <ul className="mt-4 space-y-2.5 text-sm text-mist">
              {NAV_FOOTER_LINKS.map((l) => (
                <li key={l.href}>
                  <a href={l.href} className="hover:text-white">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-gold-bright">
              Contact
            </p>
            <ul className="mt-4 space-y-2.5 text-sm text-mist">
              <li className="flex items-start gap-2">
                <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-white/40" />
                <span>{CONTACT.location}</span>
              </li>
              <li className="flex items-start gap-2">
                <Phone className="mt-0.5 h-4 w-4 shrink-0 text-white/40" />
                <a href={`tel:${CONTACT.phone.replace(/\s/g, "")}`} className="hover:text-white">
                  {CONTACT.phone}
                </a>
              </li>
            </ul>

            <p className="mt-6 font-mono text-[11px] uppercase tracking-[0.2em] text-gold-bright">
              Follow Bengal Tigers
            </p>
            <div className="mt-4 flex gap-3">
              <a
                href={CONTACT.facebookUrl}
                target="_blank"
                rel="noreferrer"
                aria-label="Facebook"
                className="flex h-10 w-10 items-center justify-center rounded-full border border-line bg-navy-panel text-mist hover:border-crimson/50 hover:text-white"
              >
                <Facebook className="h-4 w-4" />
              </a>
              <a
                href={CONTACT.instagramUrl}
                target="_blank"
                rel="noreferrer"
                aria-label="Instagram"
                className="flex h-10 w-10 items-center justify-center rounded-full border border-line bg-navy-panel text-mist hover:border-crimson/50 hover:text-white"
              >
                <Instagram className="h-4 w-4" />
              </a>
              <a
                href={CONTACT.linkedinUrl}
                target="_blank"
                rel="noreferrer"
                aria-label="LinkedIn"
                className="flex h-10 w-10 items-center justify-center rounded-full border border-line bg-navy-panel text-mist hover:border-crimson/50 hover:text-white"
              >
                <Linkedin className="h-4 w-4" />
              </a>
            </div>
          </div>
        </div>

        <div className="mt-14 flex flex-col items-start justify-between gap-4 border-t border-line pt-8 sm:flex-row sm:items-center">
          <p className="text-xs text-mist">
            © {new Date().getFullYear()} Bengal Tigers CCL. All rights
            reserved.
          </p>
          <p className="text-xs text-mist">
            Celebrity Cricket League · Official Franchise
          </p>
        </div>
      </div>
    </footer>
  );
}

export default SiteFooter;
