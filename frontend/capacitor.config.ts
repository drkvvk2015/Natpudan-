import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.natpudan.medical',
  appName: 'Natpudan Nalam Ai Physician Assistant',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
  }
};

export default config;
