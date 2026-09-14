# Bengal Tigers — CCL Website

A React + Vite + TypeScript + Tailwind CSS rebuild of the Bengal Tigers site.
Same design, layout, content, animations, responsiveness, and images as the
single-file version — restructured into components for maintainability.

## Getting started

```bash
npm install
npm run dev       # start the dev server (http://localhost:5173)
npm run build     # type-check and produce a production build in /dist
npm run preview   # serve the production build locally to sanity-check it
npm run test:instagram
```

The static site can run without environment variables. Its live Instagram API
uses the Vercel configuration below; a checked-in snapshot remains available as
a local and outage fallback.

## Instagram feed

The live feed does not modify Git or rebuild the site:

1. Vercel Cron calls the protected `/api/instagram_cron` function once per day
   at 00:00 UTC.
2. The function uses `gallery-dl`, sorts by publication date so old pinned posts
   do not displace new posts, and writes the newest six posts to one private
   Vercel Blob JSON object.
3. The public, read-only `/api/instagram` function serves that stored snapshot.
   Its response is cached on Vercel's CDN for five minutes.
4. The Vite frontend requests `/api/instagram`. During plain local Vite
   development, or if the API is unavailable, it falls back to the checked-in
   `/data/instagram-posts.json` snapshot and local thumbnails.

`vercel.json` registers the function duration and the `0 0 * * *` schedule,
which is compatible with Vercel Hobby's one-cron-invocation-per-day limit.

Install and run the fetcher locally with:

```bash
python -m pip install -r requirements.txt
npm run refresh:instagram
```

`npm run refresh:instagram` refreshes only the checked-in local fallback. With
the Vercel Blob environment variables available, `npm run publish:instagram`
publishes the dynamic backend snapshot instead.

### Vercel configuration

Before deploying:

1. Create a **private Vercel Blob** store and connect it to the project. Vercel
   supplies `BLOB_READ_WRITE_TOKEN`.
2. Add a random `CRON_SECRET` of at least 16 characters. Vercel automatically
   sends it as `Authorization: Bearer …` to the cron function.
3. Add `INSTAGRAM_COOKIES_B64` as described below, because Instagram commonly
   blocks anonymous automated requests.

The Blob contains only public Instagram post metadata. Keeping it private makes
`/api/instagram` the stable public contract and allows the bundled snapshot to
take over automatically if Blob is unavailable.

Instagram frequently rate-limits anonymous automation. If a public fetch is
blocked, export a logged-in Instagram session to a Netscape cookie file and set
either `INSTAGRAM_COOKIES_FILE` locally or the base64-encoded contents as the
Vercel environment variable `INSTAGRAM_COOKIES_B64`. Cookie files matching
`.instagram-cookies*` are gitignored and must never be committed.

One way to create the narrowly scoped file with gallery-dl is:

```bash
gallery-dl --cookies-from-browser "chrome/instagram.com" \
  --cookies-export .instagram-cookies.txt \
  "https://www.instagram.com/bengaltigers.ccl/posts/"
```

On PowerShell, create the secret value without printing it to the terminal:

```powershell
[Convert]::ToBase64String(
  [IO.File]::ReadAllBytes(".instagram-cookies.txt")
) | Set-Clipboard
$env:INSTAGRAM_COOKIES_FILE = (Resolve-Path ".instagram-cookies.txt")
```

Add the clipboard value as `INSTAGRAM_COOKIES_B64` in the Vercel project.
Rotate the value when the Instagram session expires.

## Project structure

```
index.html                  Vite entry HTML (loads src/main.tsx)
src/
  main.tsx                  React root, mounts <Page />
  index.css                 Tailwind directives + global base styles
  vite-env.d.ts              Vite/asset type declarations

  app/
    page.tsx                 Top-level composition: <Navbar /> + all sections, in order

  components/
    navbar.tsx                Sticky nav bar (logo, links, social icons)

    sections/                 One file per page section, in page order
      hero.tsx                 KineticGrid hero, headline, CTAs, season record
      owners.tsx                3 GlowCards for the team owners
      about.tsx                 "Pride of Bengal. Passion for Cricket." + pillar cards
      stats.tsx                 Crimson stats banner with animated counters
      roster.tsx                Player carousel section wrapper
      head-coach.tsx            Dedicated Head Coach highlight panel
      faq.tsx                   CCL Wildcard accordion with registration CTA
      instagram-feed.tsx        Fetches the dynamic API with a static fallback
      site-footer.tsx           Footer: logo, links, contact, socials

    ui/                       Reusable building blocks
      kinetic-grid.tsx          Interactive canvas grid (pointer warp + click ripple)
      spotlight-card.tsx        GlowCard — pointer-tracked spotlight card
      player-carousel.tsx       Draggable horizontal roster carousel
      section-tag.tsx           Small gold pill label used at the top of each section
      cycling-word.tsx          Animated word-cycle ("Driven by Strength | Passion | ...")
      animated-stat.tsx         Count-up stat used in the Stats banner
      accordion-item.tsx        Single expandable FAQ row
      claw-watermark.tsx        Decorative SVG watermark behind the About section

  data/
    site-data.ts               All copy, contact info, and image imports in one place
                                (owners, players, head coach, stats, FAQ, nav links, etc.)

  assets/                     All images (logo, hero photo, owner/player/coach photos)
  lib/utils.ts                 `cn()` class-merging helper (clsx + tailwind-merge)

public/
  data/instagram-posts.json    Local/outage fallback feed
  instagram/                   Local/outage fallback thumbnails

api/
  instagram.py                Public Blob-backed read endpoint
  instagram_cron.py           Protected refresh endpoint invoked by Vercel Cron

scripts/
  refresh_instagram.py         Extraction, Blob snapshot, and local fallback helpers
  tests/                       Deterministic parser tests

vercel.json                   Function settings and daily cron registration
requirements.txt              Python function/runtime dependencies
tailwind.config.ts            Design tokens: obsidian/navy/crimson/gold palette, fonts
postcss.config.js
vite.config.ts                Sets up the `@` → `src` path alias
tsconfig.json
```

## Editing content

Almost everything you'd want to change day-to-day — player names/photos, owner
bios, contact details, FAQ copy, stats — lives in **`src/data/site-data.ts`**.
Swap an image import or edit a string there and it flows through to the right
section automatically; you shouldn't need to touch the section components for
routine content updates.

## Notes

- Player and hero photos are bundled at their original resolution. For a
  production deploy, consider compressing them (e.g. via an image CDN or
  `vite-plugin-image-optimizer`) — the current `dist` build is correct but
  image-heavy.
- Player cards show role badges (Captain, Wicket-Keeper, All-Rounder, Batter)
  plus batting/bowling styles, restored from the UI bundle — see `PLAYERS` in
  `site-data.ts` and `PlayerCarousel` in `player-carousel.tsx`.
- The email address for the footer/contact section was left out, since no
  official one was provided — add it in `CONTACT` in `site-data.ts` when
  you have one.
