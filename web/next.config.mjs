/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbo: false,
  },
  compiler: {
    emotion: true,
  },
};

export default nextConfig;
