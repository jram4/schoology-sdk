import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './', 
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        // This ensures predictable filenames with hashes for cache busting
        entryFileNames: 'assets/index-[hash].js',
        chunkFileNames: 'assets/index-[hash].js',
        assetFileNames: 'assets/index-[hash].[ext]'
      }
    }
  }
})