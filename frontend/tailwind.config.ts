import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#05070A",
        primary: "#0D4FFF",
        secondary: "#00D4FF",
        alert: "#FF3D6E",
        textMain: "#C8D0E0",
        textSub: "#3A4560",
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
