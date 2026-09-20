"use client";

import * as React from "react";
import { Menu, X, Facebook, Instagram, Linkedin } from "lucide-react";
import { cn } from "@/lib/utils";
import logo from "@/assets/bengal-tigers-logo.svg";

const INSTAGRAM_URL = "https://www.instagram.com/bengaltigers.ccl";
const FACEBOOK_URL =
  "https://www.facebook.com/share/1HRtoBdhDM/?mibextid=wwXIfr";
const LINKEDIN_URL = "https://www.linkedin.com/company/bengal-tigers-ccl/";

const NAV_LINKS = [
  { label: "Home", href: "#top" },
  { label: "Team", href: "#roster" },
  { label: "Gallery", href: "#instagram" },
  { label: "News", href: "#ccl" },
  { label: "Contact", href: "#footer" },
];

const TigerMark: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn("flex items-center gap-2.5", className)}>
    <img src={logo} alt="Bengal Tigers crest" className="h-9 w-auto" />
    <span className="font-serif text-[15px] font-semibold leading-none tracking-wide text-white">
      BENGAL
      <span className="block text-[10px] font-medium tracking-[0.35em] text-gold">
        TIGERS
      </span>
    </span>
  </div>
);

export const Navbar: React.FC = () => {
  const [open, setOpen] = React.useState(false);
  const [scrolled, setScrolled] = React.useState(false);

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed inset-x-0 top-0 z-50 transition-colors duration-300",
        scrolled
          ? "border-b border-line bg-obsidian/85 backdrop-blur-md"
          : "border-b border-transparent bg-transparent"
      )}
    >
      <nav className="mx-auto grid h-16 max-w-7xl grid-cols-[auto_1fr_auto] items-center gap-4 px-5 md:px-8">
        <a href="#top" aria-label="Bengal Tigers home">
          <TigerMark />
        </a>

        <ul className="hidden items-center justify-center gap-8 lg:flex">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-[13px] font-medium tracking-wide text-mist transition-colors hover:text-white"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="flex items-center justify-end gap-4">
          <a
            href={FACEBOOK_URL}
            target="_blank"
            rel="noreferrer"
            aria-label="Bengal Tigers on Facebook"
            className="hidden text-mist transition-colors hover:text-white sm:inline-flex"
          >
            <Facebook className="h-[18px] w-[18px]" />
          </a>
          <a
            href={INSTAGRAM_URL}
            target="_blank"
            rel="noreferrer"
            aria-label="Bengal Tigers on Instagram"
            className="hidden text-mist transition-colors hover:text-white sm:inline-flex"
          >
            <Instagram className="h-[18px] w-[18px]" />
          </a>
          <a
            href={LINKEDIN_URL}
            target="_blank"
            rel="noreferrer"
            aria-label="Bengal Tigers on LinkedIn"
            className="hidden text-mist transition-colors hover:text-white sm:inline-flex"
          >
            <Linkedin className="h-[18px] w-[18px]" />
          </a>

          <button
            className="text-white lg:hidden"
            aria-label={open ? "Close menu" : "Open menu"}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </nav>

      {open && (
        <div className="border-t border-line bg-obsidian/95 backdrop-blur-md lg:hidden">
          <ul className="flex flex-col gap-1 px-5 py-4">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="block rounded-lg px-2 py-2.5 text-sm font-medium text-mist hover:bg-white/5 hover:text-white"
                >
                  {link.label}
                </a>
              </li>
            ))}
            <li className="flex items-center gap-4 px-2 pt-3">
              <a
                href={FACEBOOK_URL}
                target="_blank"
                rel="noreferrer"
                aria-label="Bengal Tigers on Facebook"
                className="text-mist transition-colors hover:text-white"
              >
                <Facebook className="h-5 w-5" />
              </a>
              <a
                href={INSTAGRAM_URL}
                target="_blank"
                rel="noreferrer"
                aria-label="Bengal Tigers on Instagram"
                className="text-mist transition-colors hover:text-white"
              >
                <Instagram className="h-5 w-5" />
              </a>
              <a
                href={LINKEDIN_URL}
                target="_blank"
                rel="noreferrer"
                aria-label="Bengal Tigers on LinkedIn"
                className="text-mist transition-colors hover:text-white"
              >
                <Linkedin className="h-5 w-5" />
              </a>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
};

export default Navbar;
