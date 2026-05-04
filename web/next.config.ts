import type { NextConfig } from "next";

const API_HOST = process.env.NEXT_PUBLIC_API_URL ?? "";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API_HOST}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
