# Building From Source - G90-SDR

Why and how to build FlRig and GQRX from source for maximum reliability.

---

## 🎯 Why Build From Source?

### **The Problem with Package Managers:**

```
System packages (apt, yum, etc.):
├── ❌ Often outdated (months or years behind)
├── ❌ Missing latest features
├── ❌ Contains known bugs that are fixed upstream
├── ❌ Breaks during system upgrades
├── ❌ Dependency conflicts
└── ❌ No control over version

Building from source:
├── ✅ Always latest stable release
├── ✅ All features available
├── ✅ Bug fixes included immediately
├── ✅ Survives system upgrades
├── ✅ Complete control
└── ✅ Optimized for YOUR system
```

### **Real-World Example:**

```bash
# Package manager version:
apt install gqrx-sdr
# Gets: GQRX 2.15.9 (from 2022)
# Missing: Features added in 2023-2024
# Has: Bugs fixed 2 years ago upstream

# Source build:
bash build_gqrx.bash
# Gets: GQRX 2.17.5 (latest stable)
# Has: All latest features
# Bug fixes: Current
```

---

## 📦 What G90-SDR Builds From Source

### **1. FlRig** (Already Built in install.bash)
- Version: 2.0.03 or latest
- Build time: ~5 minutes on Pi 5
- Reason: Package often outdated or unavailable

### **2. GQRX** (Now Built in install.bash)
- Version: Latest stable (2.17.x)
- Build time: ~15 minutes on Pi 5
- Reason: Package versions lag significantly

---

## 🔧 Building GQRX

### **Option 1: During Installation (Automatic)**

```bash
cd $L_SDR_DIR
bash install.bash
```

The installer will:
1. Detect if GQRX is installed
2. Ask if you want to rebuild from source
3. Automatically build latest stable version
4. Install to `/usr/local/bin/`

### **Option 2: Standalone Build (Manual)**

```bash
cd $L_SDR_DIR
bash build_gqrx.bash
```

Interactive script that:
- Shows current installed version
- Lists available versions
- Lets you choose which to build
- Handles all dependencies
- Installs automatically

### **Option 3: Manual Build (Advanced)**

```bash
# Install dependencies
sudo apt install -y \
    git cmake build-essential \
    qtbase5-dev libqt5svg5-dev \
    libgnuradio-dev gr-osmosdr \
    libpulse-dev portaudio19-dev \
    libsndfile1-dev libvolk2-dev \
    liblog4cpp5-dev libboost-all-dev

# Clone repository
cd /tmp
git clone https://github.com/gqrx-sdr/gqrx.git
cd gqrx

# Checkout latest stable
git checkout $(git describe --tags --abbrev=0)

# Build
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

---

## 🏗️ Building FlRig

FlRig is automatically built from source during installation.

### **Manual FlRig Build:**

```bash
# Dependencies (already in install.bash)
sudo apt install -y \
    libfltk1.3-dev \
    libfltk-images1.3 \
    libfltk-forms1.3 \
    libx11-dev

# Download and build
cd /tmp
wget https://sourceforge.net/projects/fldigi/files/flrig/flrig-2.0.03.tar.gz
tar -xzf flrig-2.0.03.tar.gz
cd flrig-2.0.03
./configure --prefix=/usr/local
make -j$(nproc)
sudo make install
```

---

## ⏱️ Build Times

### **Raspberry Pi 5 (4GB RAM):**
- FlRig: ~5 minutes
- GQRX: ~15 minutes
- **Total: ~20 minutes**

### **Raspberry Pi 4:**
- FlRig: ~8 minutes
- GQRX: ~25 minutes
- **Total: ~33 minutes**

### **Desktop PC (Intel i5/Ryzen 5):**
- FlRig: ~2 minutes
- GQRX: ~5 minutes
- **Total: ~7 minutes**

---

## 💾 Disk Space Requirements

```
Build process:
├── Source code: ~150 MB
├── Build files: ~500 MB
├── Final install: ~50 MB
└── Total during build: ~700 MB

After cleanup:
└── Installed binaries: ~50 MB
```

Plenty of room on any modern system!

---

## 🔄 Updating to Latest Version

### **Check for Updates:**

```bash
# Check current versions
flrig --version
gqrx --version

# Check latest available
# FlRig: https://sourceforge.net/projects/fldigi/files/flrig/
# GQRX: https://github.com/gqrx-sdr/gqrx/releases
```

### **Rebuild GQRX:**

```bash
cd $L_SDR_DIR
bash build_gqrx.bash
```

Select latest version when prompted.

### **Rebuild FlRig:**

```bash
cd /tmp
wget https://sourceforge.net/projects/fldigi/files/flrig/flrig-[VERSION].tar.gz
tar -xzf flrig-[VERSION].tar.gz
cd flrig-[VERSION]
./configure --prefix=/usr/local
make -j$(nproc)
sudo make install
```

---

## 🐛 Troubleshooting Builds

### **Problem: Missing Dependencies**

```bash
# Error during cmake or configure
# Solution: Install development packages

sudo apt update
sudo apt install -y build-essential cmake git

# For GQRX specifically:
sudo apt install -y \
    qtbase5-dev \
    libgnuradio-dev \
    gr-osmosdr
```

### **Problem: Out of Memory During Build**

```bash
# Raspberry Pi with limited RAM
# Solution: Use fewer cores or add swap

# Reduce cores:
make -j2  # Instead of -j$(nproc)

# Or add swap space:
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### **Problem: Build Fails with Errors**

```bash
# Clean and retry
cd build
make clean
cmake ..
make -j$(nproc)

# Or start completely fresh:
cd /tmp
rm -rf gqrx
# Start build process again
```

### **Problem: Can't Find Installed Binary**

```bash
# Check if installed
which gqrx
which flrig

# If not found, check install location
ls /usr/local/bin/gqrx
ls /usr/local/bin/flrig

# Update PATH if needed (shouldn't be necessary)
export PATH="/usr/local/bin:$PATH"

# Or log out and back in
```

---

## ✅ Verifying Builds

### **Test FlRig:**

```bash
# Check version
flrig --version

# Test connection to G90
flrig --rig-file=$L_SDR_DIR/config/flrig_g90.xml
```

### **Test GQRX:**

```bash
# Check version
gqrx --version

# Start GQRX
gqrx

# Check in About menu for version number
```

---

## 📊 Version Comparison

### **FlRig:**

| Source | Version | Date | Status |
|--------|---------|------|--------|
| Ubuntu 24.04 apt | 1.4.8 | 2022 | ❌ Outdated |
| Source build | 2.0.03 | 2024 | ✅ Current |

**Benefit:** 2 years newer, many bug fixes

### **GQRX:**

| Source | Version | Date | Status |
|--------|---------|------|--------|
| Ubuntu 24.04 apt | 2.15.9 | 2022 | ❌ Outdated |
| Source build | 2.17.5+ | 2024 | ✅ Current |

**Benefit:** New features, performance improvements

---

## 🎯 Installation Locations

### **System Package vs Source Build:**

```
Package Manager (apt):
├── Binary: /usr/bin/gqrx
├── Libraries: /usr/lib/
└── Managed by: apt/dpkg

Source Build (Our Method):
├── Binary: /usr/local/bin/gqrx
├── Libraries: /usr/local/lib/
└── Managed by: You

Priority:
└── /usr/local/bin is checked BEFORE /usr/bin
    (Your build takes precedence automatically)
```

---

## 🔧 Maintenance

### **Keep Builds Updated:**

```bash
# Quarterly update schedule recommended
# Check for new versions every 3 months

# Update GQRX:
bash build_gqrx.bash

# Update FlRig:
# Check https://sourceforge.net/projects/fldigi/files/flrig/
# Download and build new version
```

### **Remove Source Builds:**

```bash
# To remove and revert to packages:
sudo rm /usr/local/bin/gqrx
sudo rm /usr/local/bin/flrig
sudo apt install gqrx-sdr flrig

# (Not recommended - you'll get old versions)
```

---

## 📚 Additional Resources

### **Official Documentation:**

**GQRX:**
- GitHub: https://github.com/gqrx-sdr/gqrx
- Releases: https://github.com/gqrx-sdr/gqrx/releases
- Build guide: https://github.com/gqrx-sdr/gqrx/blob/master/README.md

**FlRig:**
- SourceForge: https://sourceforge.net/projects/fldigi/files/flrig/
- Documentation: http://www.w1hkj.com/flrig-help/

---

## 💪 Benefits Summary

### **Why This Approach is Superior:**

1. ✅ **Latest Features** - Always up-to-date
2. ✅ **Bug Fixes** - Current patches applied
3. ✅ **Stability** - No package manager conflicts
4. ✅ **Control** - You choose when to update
5. ✅ **Performance** - Optimized for your CPU
6. ✅ **Reliability** - Survives system upgrades
7. ✅ **Professional** - Industry best practice

### **Trade-offs:**

- ⏱️ Takes 20 minutes to build (one-time)
- 💾 Uses more disk space during build
- 🔄 Manual updates (but controlled by you)

**The benefits FAR outweigh the minimal cost.**

---

## 🎖️ Professional Standard

Building from source is what professionals do:

- **Server administrators** build from source for stability
- **Security experts** build from source for control
- **Embedded developers** build from source for optimization
- **You** build from source for **reliability**

**This is the RIGHT way to do it.**

---

**Your G90-SDR system is built on a foundation of current, stable, controlled software.**

**No outdated packages. No surprises. No breakage.**

**73!** 📻✨
