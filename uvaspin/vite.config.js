import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  css: {
    preprocessorOptions: {
      css: {
        additionalData: `@import "./src/assets/css/variables.css";`
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 6000,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'react-router': ['react-router-dom'],
          'plotly': ['plotly.js-basic-dist', 'react-plotly.js'],
          'mui': ['@mui/material', '@mui/x-date-pickers', '@emotion/react', '@emotion/styled'],
          'date-utils': ['dayjs', 'moment', 'react-datepicker', 'react-date-picker', 'react-time-picker']
        }
      }
    },
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
    'process.env': '{}'
  },
  resolve: {
    alias: {
      'buffer': 'buffer',
      'stream': 'stream-browserify',
      'util': 'util'
    }
  }
})
