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
```

No environment variables or extra setup are required — all images live in
`src/assets` and are bundled by Vite.

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
      about.tsx                 "Carrying Bengal's Pride" + pillar cards
      stats.tsx                 Crimson stats banner with animated counters
      roster.tsx                Player carousel section wrapper
      head-coach.tsx            Dedicated Head Coach highlight panel
      faq.tsx                   CCL & Wildcards accordion
      instagram-feed.tsx        Instagram post grid
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
- Roles/positions (Batsman, Bowler, etc.) were intentionally removed from the
  player cards per a later revision — only name and jersey number are shown.
- The email address for the footer/contact section was left out, since no
  official one was provided — add it in `CONTACT` in `site-data.ts` when
  you have one.
