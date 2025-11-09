import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBase = env.VITE_API_BASE_URL || env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'
  const wsBase = env.VITE_WS_URL || apiBase.replace('http', 'ws')
  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: apiBase,
          changeOrigin: true,
        },
        '/health': {
          target: apiBase,
          changeOrigin: true,
        },
        '/ws': {
          target: wsBase,
          ws: true,
        },
      },
    },
    preview: {
      port: 3000,
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'mui-vendor': ['@mui/material', '@mui/icons-material', '@emotion/react', '@emotion/styled'],
            'axios-vendor': ['axios'],
          },
        },
      },
      chunkSizeWarningLimit: 600,
    },
  }
})

