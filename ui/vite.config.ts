import { defineConfig } from "vitest/config";
import type { Plugin } from "vite";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";

// The Go server templates index.html with custom delimiters "/[[" and "]]"
// (see static.go renderIndexFile). The base path below must survive the build
// verbatim; if Vite ever URL-encodes the square brackets, decode them back so
// the Go template engine can still find its actions. Idempotent.
function goTemplateBaseGuard(): Plugin {
  return {
    name: "go-template-base-guard",
    transformIndexHtml(html) {
      return html.replaceAll("%5B%5B", "[[").replaceAll("%5D%5D", "]]");
    },
  };
}

export default defineConfig({
  base: "/[[.RootPath]]/",
  plugins: [react(), svgr(), goTemplateBaseGuard()],
  build: {
    outDir: "build",
    emptyOutDir: true,
  },
  server: {
    // Mirror the CRA dev behavior: the UI dev server talks to a local
    // asynqmon API (api.ts hits http://localhost:8080 in development).
    proxy: {
      "/api": "http://localhost:8080",
    },
  },
  test: {
    environment: "jsdom",
  },
});
