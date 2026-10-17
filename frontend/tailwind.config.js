/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--bg-body)",
        surface: "var(--bg-surface)",
        card: "var(--bg-card)",
        "card-hover": "var(--bg-card-hover)",
        border: "var(--border-color)",
        "border-hover": "var(--border-hover)",
        primary: {
          DEFAULT: "var(--primary)",
          hover: "var(--primary-hover)",
          inverse: "var(--primary-inverse)",
        },
        orange: {
          DEFAULT: "var(--orange)",
          light: "var(--orange-light)",
          glow: "var(--orange-glow)",
          subtle: "var(--orange-subtle)",
        },
        blue: {
          DEFAULT: "var(--blue)",
          subtle: "var(--blue-subtle)",
        },
        emerald: {
          DEFAULT: "var(--emerald)",
        },
        text: {
          primary: "var(--text-primary)",
          secondary: "var(--text-secondary)",
          muted: "var(--text-muted)",
        }
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        full: "var(--radius-full)",
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
        mono: ["var(--font-mono)"],
      }
    },
  },
  plugins: [],
}
