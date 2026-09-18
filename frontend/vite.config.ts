import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

const APP_MOUNT_PATH = "/slidegen";

const slidegenMountPlugin: Plugin = {
  name: "slidegen-mount-path",
  configureServer(server) {
    server.middlewares.use((request, _response, next) => {
      if (request.url === APP_MOUNT_PATH || request.url?.startsWith(`${APP_MOUNT_PATH}/`)) {
        request.url = request.url.slice(APP_MOUNT_PATH.length) || "/";
      }
      next();
    });
  },
  configurePreviewServer(server) {
    server.middlewares.use((request, _response, next) => {
      if (request.url === APP_MOUNT_PATH || request.url?.startsWith(`${APP_MOUNT_PATH}/`)) {
        request.url = request.url.slice(APP_MOUNT_PATH.length) || "/";
      }
      next();
    });
  },
};

// https://vitejs.dev/config/
export default defineConfig(() => ({
  // The FE is mounted below /slidegen in production. Relative build assets
  // keep the same bundle usable at that mount point without hard-coded roots.
  base: "./",
  server: {
    host: "::",
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:12008",
        changeOrigin: true,
      },
    },
    hmr: {
      overlay: false,
    },
  },
  plugins: [react(), slidegenMountPlugin],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
