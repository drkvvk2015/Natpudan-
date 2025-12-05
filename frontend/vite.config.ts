import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  // Load SSL certificates for HTTPS dev server
  const certPath = path.resolve(__dirname, 'certs/cert.pem')
  const keyPath = path.resolve(__dirname, 'certs/key.pem')
  const httpsConfig = fs.existsSync(certPath) && fs.existsSync(keyPath) ? {
    key: fs.readFileSync(keyPath),
    cert: fs.readFileSync(certPath)
  } : false
  
  return {
    plugins: [react()],
    server: {
      https: false, // Temporarily disable HTTPS to avoid WebSocket issues with Node v22
      host: '127.0.0.1',
      port: 5173,
      strictPort: true,
      hmr: {
        overlay: false, // Disable error overlay that uses WebSocket
      },
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
      // No proxy - frontend makes direct API calls to backend
    },
    preview: {
      https: httpsConfig,
      host: '127.0.0.1',
      port: 3000,
      strictPort: true,
      // No proxy - direct API calls
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'mui-vendor': ['@mui/material', '@emotion/react', '@emotion/styled'],
          },
        },
      },
      chunkSizeWarningLimit: 600,
    },
    esbuild: {
      drop: mode === 'production' ? ['console', 'debugger'] : [],
    },
  }
})

