import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-outfit)", "system-ui", "sans-serif"],
        display: ["var(--font-fraunces)", "serif"],
      },
      colors: {
        ink: {
          950: "#07090d",
          900: "#0e131b",
          800: "#161d28",
          700: "#1e2836",
        },
        sand: "#f3e6d0",
        ember: "#e85d04",
        moss: "#7d9b76",
      },
    },
  },
  plugins: [],
};

export default config;
