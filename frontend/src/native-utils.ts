// Capacitor Native Plugin Utilities
// Provides abstraction for native device features

import { Capacitor } from '@capacitor/core';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Geolocation, Position } from '@capacitor/geolocation';
import { Device, DeviceInfo } from '@capacitor/device';
import { Network, ConnectionStatus } from '@capacitor/network';
import { Haptics, ImpactStyle } from '@capacitor/haptics';
import { StatusBar, Style } from '@capacitor/status-bar';
import { Keyboard } from '@capacitor/keyboard';
import { Share } from '@capacitor/share';
import { Toast } from '@capacitor/toast';

export const isNative = Capacitor.isNativePlatform();
export const platform = Capacitor.getPlatform();

/**
 * Camera utilities
 */
export async function takePicture(): Promise<string | null> {
  try {
    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.DataUrl,
      source: CameraSource.Camera,
    });
    return image.dataUrl || null;
  } catch (error) {
    console.error('[Native] Camera error:', error);
    return null;
  }
}

export async function pickImage(): Promise<string | null> {
  try {
    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.DataUrl,
      source: CameraSource.Photos,
    });
    return image.dataUrl || null;
  } catch (error) {
    console.error('[Native] Image picker error:', error);
    return null;
  }
}

/**
 * Geolocation utilities
 */
export async function getCurrentLocation(): Promise<Position | null> {
  try {
    const position = await Geolocation.getCurrentPosition({
      enableHighAccuracy: true,
      timeout: 10000,
    });
    return position;
  } catch (error) {
    console.error('[Native] Geolocation error:', error);
    return null;
  }
}

export async function watchLocation(
  callback: (position: Position) => void
): Promise<string> {
  const id = await Geolocation.watchPosition(
    { enableHighAccuracy: true },
    (position) => {
      if (position) callback(position);
    }
  );
  return id;
}

export async function clearLocationWatch(id: string): Promise<void> {
  await Geolocation.clearWatch({ id });
}

/**
 * Device information
 */
export async function getDeviceInfo(): Promise<DeviceInfo> {
  return await Device.getInfo();
}

export async function getDeviceId(): Promise<string> {
  const info = await Device.getId();
  return info.identifier;
}

export async function getBatteryInfo() {
  return await Device.getBatteryInfo();
}

/**
 * Network utilities
 */
export async function getNetworkStatus(): Promise<ConnectionStatus> {
  return await Network.getStatus();
}

export function onNetworkChange(
  callback: (status: ConnectionStatus) => void
): void {
  Network.addListener('networkStatusChange', callback);
}

/**
 * Haptic feedback
 */
export async function hapticImpact(style: ImpactStyle = ImpactStyle.Medium): Promise<void> {
  if (isNative) {
    await Haptics.impact({ style });
  }
}

export async function hapticVibrate(duration: number = 300): Promise<void> {
  if (isNative) {
    await Haptics.vibrate({ duration });
  }
}

export async function hapticNotification(type: 'success' | 'warning' | 'error'): Promise<void> {
  if (isNative) {
    await Haptics.notification({ type: type.toUpperCase() as any });
  }
}

/**
 * Status bar utilities
 */
export async function setStatusBarStyle(isDark: boolean): Promise<void> {
  if (isNative) {
    await StatusBar.setStyle({
      style: isDark ? Style.Dark : Style.Light,
    });
  }
}

export async function hideStatusBar(): Promise<void> {
  if (isNative) {
    await StatusBar.hide();
  }
}

export async function showStatusBar(): Promise<void> {
  if (isNative) {
    await StatusBar.show();
  }
}

/**
 * Keyboard utilities
 */
export async function hideKeyboard(): Promise<void> {
  if (isNative) {
    await Keyboard.hide();
  }
}

export function onKeyboardShow(callback: (info: any) => void): void {
  if (isNative) {
    Keyboard.addListener('keyboardWillShow', callback);
  }
}

export function onKeyboardHide(callback: () => void): void {
  if (isNative) {
    Keyboard.addListener('keyboardWillHide', callback);
  }
}

/**
 * Share utilities
 */
export async function shareText(text: string, title?: string): Promise<void> {
  try {
    await Share.share({
      title: title || 'Share',
      text,
      dialogTitle: 'Share medical information',
    });
  } catch (error) {
    console.error('[Native] Share error:', error);
  }
}

export async function shareFile(
  url: string,
  title?: string
): Promise<void> {
  try {
    await Share.share({
      title: title || 'Share',
      url,
      dialogTitle: 'Share medical document',
    });
  } catch (error) {
    console.error('[Native] Share error:', error);
  }
}

/**
 * Toast notifications
 */
export async function showToast(
  text: string,
  duration: 'short' | 'long' = 'short'
): Promise<void> {
  await Toast.show({
    text,
    duration,
  });
}

/**
 * Check platform capabilities
 */
export function checkNativeFeatures() {
  return {
    isNative: isNative,
    platform: platform,
    camera: Capacitor.isPluginAvailable('Camera'),
    geolocation: Capacitor.isPluginAvailable('Geolocation'),
    device: Capacitor.isPluginAvailable('Device'),
    network: Capacitor.isPluginAvailable('Network'),
    haptics: Capacitor.isPluginAvailable('Haptics'),
    statusBar: Capacitor.isPluginAvailable('StatusBar'),
    keyboard: Capacitor.isPluginAvailable('Keyboard'),
    share: Capacitor.isPluginAvailable('Share'),
    toast: Capacitor.isPluginAvailable('Toast'),
  };
}
