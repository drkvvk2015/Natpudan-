#!/usr/bin/env node
/**
 * Cross-platform Android build script
 * Automatically uses gradlew.bat on Windows or ./gradlew on Unix
 */

import { exec } from 'child_process';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const isWindows = os.platform() === 'win32';
const gradleCommand = isWindows ? 'gradlew.bat' : './gradlew';

console.log(`🔨 Building Android APK...`);
console.log(`Platform: ${os.platform()}`);
console.log(`Using: ${gradleCommand}`);

// Build steps
const steps = [
  {
    name: 'Build web assets',
    command: 'npm run build:web',
    cwd: __dirname
  },
  {
    name: 'Sync Capacitor',
    command: 'npx cap sync android',
    cwd: __dirname
  },
  {
    name: 'Build Android APK',
    command: `${gradleCommand} assembleRelease`,
    cwd: path.join(__dirname, 'android')
  }
];

// Execute steps sequentially
async function runSteps() {
  for (const step of steps) {
    console.log(`\n📦 ${step.name}...`);
    
    try {
      await new Promise((resolve, reject) => {
        const child = exec(step.command, { cwd: step.cwd }, (error, stdout, stderr) => {
          if (error) {
            reject(error);
          } else {
            resolve();
          }
        });

        child.stdout.pipe(process.stdout);
        child.stderr.pipe(process.stderr);
      });
      
      console.log(`✅ ${step.name} completed`);
    } catch (error) {
      console.error(`\n❌ ${step.name} failed:`);
      console.error(error.message);
      process.exit(1);
    }
  }

  console.log(`\n✅ Android build completed successfully!`);
  console.log(`\n📱 APK location: android/app/build/outputs/apk/release/app-release.apk`);
}

runSteps();
