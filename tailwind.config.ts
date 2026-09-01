import type { Config } from "tailwindcss";

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        obsidian: "#060C18",
        navy: {
          DEFAULT: "#0A111E",
          panel: "#0E1726",
        },
        crimson: {
          DEFAULT: "#B91C1C",
          bright: "#C81E1E",
          deep: "#7F1D1D",
        },
        gold: {
          DEFAULT: "#D4AF37",
          bright: "#E5C158",
        },
        mist: "#94A3B8",
        line: "#16202F",
      },
      fontFamily: {
        serif: ["Fraunces", "Georgia", "serif"],
        sans: ["Manrope", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
