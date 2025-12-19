import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
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
    plugins: [
      react(),
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.svg', 'logo-icon.svg', 'icon-192x192.png', 'icon-512x512.png'],
        manifest: false, // Use existing public/manifest.json
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
          runtimeCaching: [
            {
              urlPattern: /^\/api\/medical\/knowledge\//,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'medical-knowledge-api',
                expiration: {
                  maxEntries: 50,
                  maxAgeSeconds: 60 * 60 * 24 // 24 hours
                },
                cacheableResponse: {
                  statuses: [0, 200]
                }
              }
            },
            {
              urlPattern: /^\/api\/(auth|chat|diagnosis|prescription)/,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'critical-api',
                expiration: {
                  maxEntries: 100,
                  maxAgeSeconds: 60 * 5 // 5 minutes
                },
                networkTimeoutSeconds: 10
              }
            },
            {
              urlPattern: /^\/api\/(analytics|timeline|treatment)/,
              handler: 'StaleWhileRevalidate',
              options: {
                cacheName: 'non-critical-api',
                expiration: {
                  maxEntries: 50,
                  maxAgeSeconds: 60 * 30 // 30 minutes
                }
              }
            },
            {
              urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'google-fonts-cache',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
                },
                cacheableResponse: {
                  statuses: [0, 200]
                }
              }
            },
            {
              urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
              handler: 'CacheFirst',
              options: {
                cacheName: 'images-cache',
                expiration: {
                  maxEntries: 100,
                  maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
                }
              }
            }
          ],
          cleanupOutdatedCaches: true,
          skipWaiting: true,
          clientsClaim: true
        },
        devOptions: {
          enabled: false // Disable PWA in dev mode
        }
      })
    ],
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
      outDir: 'dist',
      sourcemap: mode === 'production' ? false : true,
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: mode === 'production',
          drop_debugger: mode === 'production',
          pure_funcs: mode === 'production' ? ['console.log', 'console.debug'] : []
        }
      },
      rollupOptions: {
        output: {
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'mui-vendor': ['@mui/material', '@emotion/react', '@emotion/styled'],
            'mui-icons': ['@mui/icons-material'],
            'chart-vendor': ['recharts'],
            'utils': ['axios', 'date-fns']
          },
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.');
            const ext = info[info.length - 1];
            if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext)) {
              return `assets/images/[name]-[hash][extname]`;
            } else if (/woff|woff2/.test(ext)) {
              return `assets/fonts/[name]-[hash][extname]`;
            }
            return `assets/[name]-[hash][extname]`;
          },
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js'
        },
      },
      chunkSizeWarningLimit: 1000,
      reportCompressedSize: false,
    },
    esbuild: {
      drop: mode === 'production' ? ['console', 'debugger'] : [],
    },
  }
})

