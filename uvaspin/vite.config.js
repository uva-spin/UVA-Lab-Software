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
    port: 5000,
    open: true,
    host: true,
    proxy: {
      '/query_db': {
        target: process.env.VITE_API_URL,
        changeOrigin: true,
        secure: false
      },
      '/health_check': {
        target: process.env.VITE_API_URL,
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    commonjsOptions: {
      transformMixedEsModules: true
    }
  },
  optimizeDeps: {
    include: ['plotly.js-basic-dist', 'react-plotly.js'],
    exclude: ['buffer']
  },
  define: {
    global: 'globalThis',
    'process.env': '{}',
    'require': '(() => { throw new Error("require is not defined in browser environment") })'
  },
  resolve: {
    alias: {
      'buffer': 'buffer',
      'stream': 'stream-browserify',
      'util': 'util'
    }
  }
})
