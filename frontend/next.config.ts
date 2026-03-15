import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  typescript: {
    ignoreBuildErrors: false,
  },
  // Poll-based watching for Docker on Windows — inotify events don't cross
  // the host→container bind-mount boundary over SMB/CIFS.
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 500,
        aggregateTimeout: 300,
      };
    }
    return config;
  },
  // Ensure we can build despite the webpack config under Turbopack
  turbopack: {},
};

export default nextConfig;
