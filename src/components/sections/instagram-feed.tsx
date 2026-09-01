import * as React from "react";
import { Instagram, Heart, MessageCircle, ArrowUpRight } from "lucide-react";

import { SectionTag } from "@/components/ui/section-tag";
import { CONTACT, INSTAGRAM_POSTS } from "@/data/site-data";

export function InstagramFeed() {
  return (
    <section id="instagram" className="border-t border-line py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <SectionTag>{CONTACT.instagramHandle}</SectionTag>
            <h2 className="mt-4 font-serif text-3xl font-semibold text-white sm:text-4xl">
              Latest from Instagram
            </h2>
          </div>
          <a
            href={CONTACT.instagramUrl}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 text-sm font-medium text-gold-bright hover:text-white"
          >
            Follow along <ArrowUpRight className="h-4 w-4" />
          </a>
        </div>

        <div className="mt-12 grid grid-cols-2 gap-4 sm:grid-cols-3">
          {INSTAGRAM_POSTS.map((post, i) => (
            <div
              key={i}
              className="group relative aspect-square overflow-hidden rounded-xl border border-line bg-navy-panel"
            >
              <div className="absolute inset-0 flex items-center justify-center text-white/10">
                <Instagram className="h-8 w-8" />
              </div>

              {post.iconic && (
                <span className="absolute left-3 top-3 z-10 rounded-full bg-gold px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-navy">
                  Iconic Moment
                </span>
              )}

              <div className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-black/90 via-black/10 to-transparent p-4 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                <p className="text-sm font-medium text-white">
                  {post.caption}
                </p>
                <div className="mt-2 flex items-center gap-4 text-xs text-white/70">
                  <span className="flex items-center gap-1">
                    <Heart className="h-3.5 w-3.5" /> {post.likes}
                  </span>
                  <span className="flex items-center gap-1">
                    <MessageCircle className="h-3.5 w-3.5" /> {post.comments}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default InstagramFeed;
