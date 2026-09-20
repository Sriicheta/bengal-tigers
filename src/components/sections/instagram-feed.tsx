import * as React from "react";
import {
  ArrowUpRight,
  Heart,
  Instagram,
  MessageCircle,
  Play,
} from "lucide-react";

import { SectionTag } from "@/components/ui/section-tag";
import { CONTACT } from "@/data/site-data";

type InstagramPost = {
  id: string;
  shortcode: string;
  url: string;
  caption: string;
  image: string;
  publishedAt: string;
  likes: number | null;
  comments: number | null;
  type: "post" | "reel";
};

type InstagramFeedData = {
  account: {
    username: string;
    handle: string;
    url: string;
  };
  fetchedAt: string;
  posts: InstagramPost[];
};

const NUMBER_FORMATTER = new Intl.NumberFormat("en", {
  notation: "compact",
  maximumFractionDigits: 1,
});

const DATE_FORMATTER = new Intl.DateTimeFormat("en", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

function isInstagramFeed(value: unknown): value is InstagramFeedData {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<InstagramFeedData>;
  return Array.isArray(candidate.posts) && candidate.posts.length > 0;
}

function firstLine(caption: string) {
  return caption.split("\n").find((line) => line.trim())?.trim() || "View this post on Instagram";
}

function formatDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Latest post" : DATE_FORMATTER.format(date);
}

function LoadingCards() {
  return (
    <div className="mt-12 grid grid-cols-2 gap-4 sm:grid-cols-3" aria-label="Loading Instagram posts">
      {Array.from({ length: 6 }, (_, index) => (
        <div
          key={index}
          className="aspect-square animate-pulse rounded-xl border border-line bg-navy-panel"
        />
      ))}
    </div>
  );
}

export function InstagramFeed() {
  const [feed, setFeed] = React.useState<InstagramFeedData | null>(null);
  const [failed, setFailed] = React.useState(false);

  React.useEffect(() => {
    const controller = new AbortController();

    async function loadFeed() {
      for (const url of ["/api/instagram", "/data/instagram-posts.json"]) {
        try {
          const response = await fetch(url, { signal: controller.signal });
          if (!response.ok) continue;

          const data: unknown = await response.json();
          if (!isInstagramFeed(data)) continue;
          setFeed(data);
          return;
        } catch (error) {
          if (error instanceof DOMException && error.name === "AbortError") return;
        }
      }

      setFailed(true);
    }

    void loadFeed();
    return () => controller.abort();
  }, []);

  return (
    <section id="instagram" className="border-t border-line py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <SectionTag>{feed?.account.handle ?? CONTACT.instagramHandle}</SectionTag>
            <h2 className="mt-4 font-serif text-3xl font-semibold text-white sm:text-4xl">
              Latest on Media
            </h2>
            <p className="mt-3 max-w-xl text-sm leading-6 text-white/55">
              Matchday energy, squad news and the newest Bengal Tigers moments.
            </p>
          </div>
          <a
            href={feed?.account.url ?? CONTACT.instagramUrl}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 text-sm font-medium text-gold-bright hover:text-white"
          >
            Follow along <ArrowUpRight className="h-4 w-4" />
          </a>
        </div>

        {!feed && !failed && <LoadingCards />}

        {failed && (
          <a
            href={CONTACT.instagramUrl}
            target="_blank"
            rel="noreferrer"
            className="mt-12 flex min-h-52 items-center justify-center rounded-xl border border-line bg-navy-panel px-6 text-center text-sm text-white/65 transition-colors hover:border-gold/40 hover:text-white"
          >
            The feed is taking a timeout. Open Instagram to see the latest posts.
            <ArrowUpRight className="ml-2 h-4 w-4" />
          </a>
        )}

        {feed && (
          <div className="mt-12 grid grid-cols-2 gap-4 sm:grid-cols-3">
            {feed.posts.map((post) => (
              <a
                key={post.id}
                href={post.url}
                target="_blank"
                rel="noreferrer"
                aria-label={`Open Instagram post from ${formatDate(post.publishedAt)}`}
                className="group relative aspect-square overflow-hidden rounded-xl border border-line bg-navy-panel"
              >
                <img
                  src={post.image}
                  alt={firstLine(post.caption)}
                  loading="lazy"
                  className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.04]"
                />

                <span className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-black/60 text-white backdrop-blur-sm">
                  {post.type === "reel" ? (
                    <Play className="h-3.5 w-3.5 fill-current" aria-label="Reel" />
                  ) : (
                    <Instagram className="h-4 w-4" aria-label="Post" />
                  )}
                </span>

                <div className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-black via-black/20 to-transparent p-3 transition-colors sm:p-4">
                  <time dateTime={post.publishedAt} className="text-[10px] font-semibold uppercase tracking-[0.14em] text-gold-bright">
                    {formatDate(post.publishedAt)}
                  </time>
                  <p className="mt-1 line-clamp-2 text-xs font-medium leading-5 text-white sm:text-sm">
                    {firstLine(post.caption)}
                  </p>
                  {(post.likes !== null || post.comments !== null) && (
                    <div className="mt-2 flex items-center gap-3 text-[11px] text-white/70">
                      {post.likes !== null && (
                        <span className="flex items-center gap-1">
                          <Heart className="h-3.5 w-3.5" /> {NUMBER_FORMATTER.format(post.likes)}
                        </span>
                      )}
                      {post.comments !== null && (
                        <span className="flex items-center gap-1">
                          <MessageCircle className="h-3.5 w-3.5" /> {NUMBER_FORMATTER.format(post.comments)}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

export default InstagramFeed;
