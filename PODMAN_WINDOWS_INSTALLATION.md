# Podman Installation for Windows

## ⚠️ Issue: Chocolatey Installation Failed

The Podman package is not available in the standard Chocolatey repository. Use one of the methods below instead.

---

## Method 1: Windows Package Manager (Recommended) ⭐

Windows Package Manager (winget) is the modern way to install Podman.

```powershell
# Install Podman via winget
winget install RedHat.Podman

# Verify installation
podman --version
```

**Time**: ~5-10 minutes

---

## Method 2: Direct Download from Podman

Download and install Podman directly from the official source.

1. **Visit**: https://podman.io/docs/installation/windows

2. **Download**: Click "Download latest release" for Windows

3. **Run installer**: Follow the installation wizard

4. **Verify in PowerShell**:
   ```powershell
   podman --version
   ```

**Time**: ~10-15 minutes

---

## Method 3: Chocolatey (Advanced - Alternative Repository)

If you want to use Chocolatey with a community package:

```powershell
# This may not work with the default repository
# Try with pre-release flag:
choco install podman --pre -y

# If that fails, download directly (Method 2)
```

---

## Next Steps After Installation

Once Podman is installed, verify it works:

```powershell
# 1. Check version
podman --version

# 2. Initialize Podman Machine
podman machine init

# 3. Start Podman Machine
podman machine start

# 4. Verify it's running
podman machine list

# 5. Install podman-compose
pip install podman-compose

# 6. Verify podman-compose
podman-compose --version

# 7. Run your application
cd d:\Users\CNSHO\Documents\GitHub\Natpudan-
.\start-podman-compose.ps1
```

---

## Troubleshooting Installation

### Issue: "winget not found"
```powershell
# winget comes with Windows 11 and Windows 10 (update 1909+)
# If not available, download the App Installer from Microsoft Store
```

### Issue: Installation hangs at "Creating machine"
```powershell
# Cancel the process and try manually:
podman machine init
podman machine start --no-graphics
```

### Issue: Permission denied during installation
```powershell
# Run PowerShell as Administrator
# Right-click on PowerShell and select "Run as administrator"
```

### Issue: Drive space needed
```powershell
# Podman machine requires ~5-10GB of disk space
# Ensure you have at least 20GB free
Get-Volume C: | Select-Object SizeRemaining
```

---

## Verify Everything Works

After installation, test with this complete script:

```powershell
# Check Podman
podman --version
podman info

# Check Podman Machine
podman machine list

# Check podman-compose
podman-compose --version

# Test simple container
podman run --rm alpine echo "Podman works!"

# Start your app
cd d:\Users\CNSHO\Documents\GitHub\Natpudan-
.\start-podman-compose.ps1
```

---

## If You Still Have Issues

1. **Completely uninstall Podman**:
   - Control Panel → Programs → Uninstall a program → Find Podman → Uninstall
   - Delete `C:\Users\[YourUser]\.podman` folder

2. **Restart your computer**

3. **Install again using Method 1 (winget)**

4. **Report the issue** with error messages

---

## References

- [Podman Windows Installation](https://podman.io/docs/installation/windows)
- [Windows Package Manager (winget)](https://learn.microsoft.com/en-us/windows/package-manager/)
- [Podman Documentation](https://docs.podman.io/)
