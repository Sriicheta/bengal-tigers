import * as React from "react";

import { Navbar } from "@/components/navbar";
import { Hero } from "@/components/sections/hero";
import { Owners } from "@/components/sections/owners";
import { About } from "@/components/sections/about";
import { Stats } from "@/components/sections/stats";
import { Roster } from "@/components/sections/roster";
import { HeadCoach } from "@/components/sections/head-coach";
import { Faq } from "@/components/sections/faq";
import { InstagramFeed } from "@/components/sections/instagram-feed";
import { SiteFooter } from "@/components/sections/site-footer";

/**
 * Page
 * ------------------------------------------------------------------
 * Top-level composition only. Each section of the site lives in its
 * own file under /components/sections; shared data and image imports
 * live in /data/site-data.ts. See README.md for the full file map.
 */
export default function Page() {
  return (
    <main id="top" className="min-h-screen bg-obsidian text-white">
      <Navbar />
      <Hero />
      <Owners />
      <About />
      <Stats />
      <Roster />
      <HeadCoach />
      <Faq />
      <InstagramFeed />
      <SiteFooter />
    </main>
  );
}
