import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
  build: {
    outDir: "../ui-dist",
    emptyOutDir: true,
    minify: "terser",
    cssCodeSplit: false,
    lib: {
      entry: "src/main.tsx",
      formats: ["es"],
      fileName: () => "synapse-pillars.js",
    },
    rollupOptions: {
      output: {
        assetFileNames: (assetInfo) =>
          assetInfo.name?.endsWith(".css") ? "synapse-pillars.css" : "[name][extname]",
      },
    },
  },
});
