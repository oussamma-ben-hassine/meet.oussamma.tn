/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: process.env.BACKEND_INTERNAL_URL 
          ? `${process.env.BACKEND_INTERNAL_URL}/api/v1/:path*`
          : 'http://backend:8000/api/v1/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
