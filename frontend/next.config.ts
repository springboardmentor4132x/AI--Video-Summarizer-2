import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/videos',
        destination: 'http://34.58.221.118:8000/videos/' 
      },
      {
        source: '/api/:path*',
        destination: 'http://34.58.221.118:8000/:path*'
      }
    ]
  }
};

export default nextConfig;
