// Electron Preload Script
// Exposes safe APIs to renderer process

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // File dialogs
  openFileDialog: (options) => ipcRenderer.invoke('open-file-dialog', options),
  saveFileDialog: (options) => ipcRenderer.invoke('save-file-dialog', options),

  // Notifications
  showNotification: (options) => ipcRenderer.invoke('show-notification', options),

  // System info
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),

  // App events
  onNewPatient: (callback) => ipcRenderer.on('new-patient', callback),
  onOpenSettings: (callback) => ipcRenderer.on('open-settings', callback),
  onOpenKnowledgeBase: (callback) => ipcRenderer.on('open-knowledge-base', callback),
  onOpenDiagnosis: (callback) => ipcRenderer.on('open-diagnosis', callback),
  onOpenDrugChecker: (callback) => ipcRenderer.on('open-drug-checker', callback),

  // Platform info
  isElectron: true,
  platform: process.platform,
});
