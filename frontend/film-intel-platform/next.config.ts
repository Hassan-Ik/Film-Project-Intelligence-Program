import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    domains: [
      "image.tmdb.org",
      "m.media-amazon.com"
    ],
  },
};

export default nextConfig;
