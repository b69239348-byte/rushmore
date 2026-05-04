import type { NextConfig } from "next";

const API_HOST = process.env.NEXT_PUBLIC_API_URL ?? "";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        // Route Handlers at /api/generate* take precedence over this rewrite.
        // If those files are deleted, requests reach the VPS without auth injection.
        source: "/api/:path*",
        destination: `${API_HOST}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
