import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: "100.72.116.128",
    port: 5173,
    proxy: { "/api": process.env.VITE_API_TARGET ?? "http://127.0.0.1:8002" },
  },
  build: { chunkSizeWarningLimit: 700 },
});
