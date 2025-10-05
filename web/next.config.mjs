/** @type {import('next').NextConfig} */
const nextConfig = {
  // 🚫 Desactivar Turbopack para evitar errores con MUI/Emotion
  experimental: {
    turbo: false,
  },
};

module.exports = nextConfig;
