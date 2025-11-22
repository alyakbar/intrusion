/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/detections/:path*',
        destination: 'http://localhost:5000/api/detections/:path*',
      },
    ]
  },
}

module.exports = nextConfig
