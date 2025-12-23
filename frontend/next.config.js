/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    serverComponentsExternalPackages: [],
    watchFileSystem: true, // enables polling for file changes
  
  },
};
module.exports = nextConfig;
