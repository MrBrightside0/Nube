/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbo: false, // Desactiva Turbopack si te está dando errores con MUI/Emotion
  },
  compiler: {
    emotion: true, // Activa soporte para Emotion
  },
};

export default nextConfig;
