import type { Config } from 'tailwindcss';

const config: Config = {
  theme: {
    extend: {
      colors: {
        'dark-gray': '#121212',   // background like black
        'maroon': '#800000',      // primary button
        'maroon-dark': '#660000', // hover
        'gray-border': '#1f1f1f', // borders for panels
      },
    },
  },
  plugins: [],
};

export default config;
