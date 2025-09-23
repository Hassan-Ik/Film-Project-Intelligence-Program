import type { Config } from 'tailwindcss';

const config: Config = {
  theme: {
    extend: {
      colors: {
        primary: "#2563EB",
        primaryHover: "#1D4ED8",
        genres: "#E9D5FF",
        genresText: "#6B21A8",
        themes: "#DCFCE7",
        themesText: "#166534",
        pitchBg: "#DBEAFE",
        pitchText: "#1E40AF",
        cardBg: "#FFFFFF",
        bgMain: "#F9FAFB",
      },
    },
  },
  plugins: [],
};

export default config;
