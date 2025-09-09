import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  css: {
    preprocessorOptions: {
      css: {
        additionalData: `@import "./css/variables.css";`
      }
    }
  },
  server: {
    port: 3000,
    open: true,
    host: true,
    proxy: {
      '/query_db': 'http://localhost:5000',
      '/health_check': 'http://localhost:5000'
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
