import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import ErrorBoundary from './components/ErrorBoundary'
import { initializeMonitoring } from './monitoring'
import './global.css'

initializeMonitoring();

// PWA imports - wrapped in try/catch for safety
try {
  console.log('[Natpudan AI] Checking PWA environment...');
  // Only load PWA features in production
  if (import.meta.env.PROD) {
    console.log('[Natpudan AI] Production mode - loading PWA...');
    import('./pwa-utils').then(({ registerServiceWorker, setupInstallPrompt, setupNetworkDetection }) => {
      // Register service worker in production
      registerServiceWorker().then((registration) => {
        if (registration) {
          console.log('[Natpudan AI] PWA features enabled');
        }
      });

      // Setup install prompt
      setupInstallPrompt(() => {
        console.log('[Natpudan AI] App can be installed');
      });

      // Setup network detection
      setupNetworkDetection(
        () => console.log('[Natpudan AI] Back online'),
        () => console.log('[Natpudan AI] Offline mode active')
      );
    }).catch(err => console.warn('[Natpudan AI] PWA features unavailable:', err));
  } else {
    console.log('[Natpudan AI] Development mode - PWA features disabled');
  }
} catch (error) {
  console.warn('[Natpudan AI] PWA initialization skipped:', error);
}

console.log('[Natpudan AI] Starting React application...');

const rootElement = document.getElementById('root');
console.log('[Natpudan AI] Root element:', rootElement);

if (!rootElement) {
  console.error('[Natpudan AI] ERROR: Root element not found!');
} else {
  try {
    console.log('[Natpudan AI] Creating React root...');
    const root = ReactDOM.createRoot(rootElement);
    
    console.log('[Natpudan AI] Rendering app...');
    root.render(
      <React.StrictMode>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      </React.StrictMode>,
    );
    console.log('[Natpudan AI] App render initiated successfully');
  } catch (error) {
    console.error('[Natpudan AI] FATAL ERROR during render:', error);
  }
}
