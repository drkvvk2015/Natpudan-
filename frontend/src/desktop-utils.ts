// Desktop utilities for Electron
// Provides desktop-specific features not available in web/mobile

export interface ElectronAPI {
  openFileDialog: (options: any) => Promise<{ canceled: boolean; filePaths: string[] }>;
  saveFileDialog: (options: any) => Promise<{ canceled: boolean; filePath: string }>;
  showNotification: (options: { title: string; body: string }) => Promise<void>;
  getSystemInfo: () => Promise<{ platform: string; arch: string; version: string; electron: string }>;
  getAppVersion: () => Promise<string>;
  onNewPatient: (callback: () => void) => void;
  onOpenSettings: (callback: () => void) => void;
  onOpenKnowledgeBase: (callback: () => void) => void;
  onOpenDiagnosis: (callback: () => void) => void;
  onOpenDrugChecker: (callback: () => void) => void;
  isElectron: boolean;
  platform: string;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

// Check if running in Electron
export const isElectron = (): boolean => {
  return !!(window.electronAPI && window.electronAPI.isElectron);
};

// Get platform
export const getDesktopPlatform = (): 'windows' | 'macos' | 'linux' | 'web' => {
  if (!isElectron()) return 'web';
  const platform = window.electronAPI!.platform;
  if (platform === 'win32') return 'windows';
  if (platform === 'darwin') return 'macos';
  if (platform === 'linux') return 'linux';
  return 'web';
};

// File dialogs
export const openFileDialog = async (options: {
  title?: string;
  defaultPath?: string;
  filters?: { name: string; extensions: string[] }[];
  properties?: ('openFile' | 'openDirectory' | 'multiSelections')[];
}): Promise<string[] | null> => {
  if (!isElectron()) {
    console.warn('File dialogs only available in desktop app');
    return null;
  }
  const result = await window.electronAPI!.openFileDialog(options);
  return result.canceled ? null : result.filePaths;
};

export const saveFileDialog = async (options: {
  title?: string;
  defaultPath?: string;
  filters?: { name: string; extensions: string[] }[];
}): Promise<string | null> => {
  if (!isElectron()) {
    console.warn('File dialogs only available in desktop app');
    return null;
  }
  const result = await window.electronAPI!.saveFileDialog(options);
  return result.canceled ? null : result.filePath;
};

// Desktop notifications
export const showDesktopNotification = async (title: string, body: string): Promise<boolean> => {
  if (isElectron()) {
    await window.electronAPI!.showNotification({ title, body });
    return true;
  }
  return false;
};

// System information
export const getSystemInfo = async (): Promise<{
  platform: string;
  arch: string;
  version: string;
  electron: string;
} | null> => {
  if (!isElectron()) return null;
  return await window.electronAPI!.getSystemInfo();
};

export const getAppVersion = async (): Promise<string> => {
  if (!isElectron()) return 'web';
  return await window.electronAPI!.getAppVersion();
};

// Menu event handlers
export const setupDesktopEventHandlers = (handlers: {
  onNewPatient?: () => void;
  onOpenSettings?: () => void;
  onOpenKnowledgeBase?: () => void;
  onOpenDiagnosis?: () => void;
  onOpenDrugChecker?: () => void;
}): void => {
  if (!isElectron()) return;

  if (handlers.onNewPatient) {
    window.electronAPI!.onNewPatient(handlers.onNewPatient);
  }
  if (handlers.onOpenSettings) {
    window.electronAPI!.onOpenSettings(handlers.onOpenSettings);
  }
  if (handlers.onOpenKnowledgeBase) {
    window.electronAPI!.onOpenKnowledgeBase(handlers.onOpenKnowledgeBase);
  }
  if (handlers.onOpenDiagnosis) {
    window.electronAPI!.onOpenDiagnosis(handlers.onOpenDiagnosis);
  }
  if (handlers.onOpenDrugChecker) {
    window.electronAPI!.onOpenDrugChecker(handlers.onOpenDrugChecker);
  }
};

// Check desktop features
export const checkDesktopFeatures = (): {
  fileDialogs: boolean;
  notifications: boolean;
  systemTray: boolean;
  autoUpdater: boolean;
} => {
  const electron = isElectron();
  return {
    fileDialogs: electron,
    notifications: electron,
    systemTray: electron,
    autoUpdater: electron,
  };
};

// Export utilities
export default {
  isElectron,
  getDesktopPlatform,
  openFileDialog,
  saveFileDialog,
  showDesktopNotification,
  getSystemInfo,
  getAppVersion,
  setupDesktopEventHandlers,
  checkDesktopFeatures,
};
