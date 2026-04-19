// Electron Preload Script
// Exposes safe APIs to renderer process

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openFileDialog: (options) => ipcRenderer.invoke('open-file-dialog', options),
  saveFileDialog: (options) => ipcRenderer.invoke('save-file-dialog', options),

  showNotification: (options) => ipcRenderer.invoke('show-notification', options),

  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),

  onNewPatient: (callback) => ipcRenderer.on('new-patient', callback),
  onOpenSettings: (callback) => ipcRenderer.on('open-settings', callback),
  onOpenKnowledgeBase: (callback) => ipcRenderer.on('open-knowledge-base', callback),
  onOpenDiagnosis: (callback) => ipcRenderer.on('open-diagnosis', callback),
  onOpenDrugChecker: (callback) => ipcRenderer.on('open-drug-checker', callback),

  isElectron: true,
  platform: process.platform,
});
