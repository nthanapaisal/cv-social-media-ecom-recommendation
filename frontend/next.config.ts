import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  skipTrailingSlashRedirect: true,
  async rewrites() {
    // BACKEND_URL is a server-side env var used by the Next.js proxy (not exposed to the browser).
    // Set it to the backend container name in Docker; it falls back to localhost for local dev.
    const backendUrl =
      process.env.BACKEND_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    return [
      {
        source: "/backend/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
