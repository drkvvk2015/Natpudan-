import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import ErrorBoundary from './components/ErrorBoundary'
import './global.css'
import { registerServiceWorker, setupInstallPrompt, setupNetworkDetection } from './pwa-utils'

// Initialize PWA features
if (import.meta.env.PROD) {
  // Register service worker in production
  registerServiceWorker().then((registration) => {
    if (registration) {
      console.log('[Natpudan AI] PWA features enabled');
    }
  });

  // Setup install prompt
  setupInstallPrompt((prompt) => {
    console.log('[Natpudan AI] App can be installed');
    // You can show a custom install button here
  });

  // Setup network detection
  setupNetworkDetection(
    () => console.log('[Natpudan AI] Back online'),
    () => console.log('[Natpudan AI] Offline mode active')
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)
