import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `http://178.104.249.211:8000/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
