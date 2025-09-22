import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  safelist: [
    'bg-blue-600', 'bg-yellow-600', 'bg-indigo-600', 'bg-green-600', 'bg-orange-500', 'bg-blue-900',
    'bg-teal-600', 'bg-orange-600', 'bg-gray-800', 'bg-blue-500', 'bg-blue-400', 'bg-black',
    'bg-cyan-600', 'bg-blue-700', 'bg-green-700', 'bg-purple-600', 'bg-green-900', 'bg-green-400',
    'bg-red-600', 'bg-orange-800', 'bg-yellow-800', 'bg-orange-700', 'bg-red-800', 'bg-blue-700'
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
    },
  },
  plugins: [],
} satisfies Config;