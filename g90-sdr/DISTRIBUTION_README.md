# G90-SDR Distribution Guide

Instructions for sharing G90-SDR with the amateur radio community.

---

## 📦 What You're Distributing

A complete software-defined radio system for the **Xiegu G90** that provides:
- Real-time waterfall display via GQRX
- Full CAT control via FlRig
- Automatic frequency synchronization
- Professional diagnostic tools
- Universal desktop launchers

---

## 🎯 Target Audience

- **Xiegu G90 owners** who want SDR functionality
- **Amateur radio operators** (all license classes)
- **Linux users** on Raspberry Pi or desktop systems
- **Technical skill level**: Beginner to Advanced

---

## 📋 System Requirements

### Hardware
- Xiegu G90 HF Transceiver
- Xiegu DE-19 Data Interface Adapter
- Computer: Raspberry Pi 5 8GB (recommended) or any Linux PC
- USB cable for DE-19 connection

### Software
- Ubuntu 24.04 LTS (or compatible Debian-based distro)
- Python 3.13+
- FlRig 2.0.03+
- GQRX 2.17+

---

## 🚀 Quick Start for End Users

### 1. Clone or Download

```bash
git clone https://github.com/YOUR_USERNAME/G90-SDR.git
cd G90-SDR
```

**Or download ZIP:**
- Download and extract to any location
- We'll call this `G90-SDR/` directory

### 2. Set Installation Path

```bash
# Add to ~/.bashrc
echo "export L_SDR_DIR=$HOME/G90-SDR" >> ~/.bashrc
source ~/.bashrc
```

**Note:** Users can install anywhere! Change path as needed:
- `$HOME/G90-SDR`
- `$HOME/Virtual/G90-SDR`
- `$HOME/Documents/G90-SDR`
- `/opt/G90-SDR` (system-wide)

### 3. Run Installation

```bash
cd $L_SDR_DIR
bash install.bash
```

This installs:
- System dependencies
- FlRig (compiles from source)
- GQRX
- Python environment
- All required packages

**Time:** 20-30 minutes on Raspberry Pi 5

### 4. Install Universal Launchers

```bash
# Create desktop launchers
bash create_universal_launchers.bash

# Install system wrappers (needs sudo)
sudo bash install_wrappers.bash
```

### 5. Reboot (Required)

```bash
sudo reboot
```

Group membership changes require reboot.

### 6. Test Installation

```bash
cd $L_SDR_DIR
source venv/bin/activate
python3 tests/TestConnection.py
python3 tests/DiagnoseSystem.py
```

### 7. Launch!

**From Applications Menu:**
- Look for "G90-SDR System" or "FlRig for G90"

**From Terminal:**
```bash
g90-sdr
```

---

## 📤 Distribution Methods

### Method 1: GitHub Repository (Recommended)

**Setup:**
```bash
cd G90-SDR
git init
git add .
git commit -m "Initial commit - G90-SDR v1.0"
git remote add origin https://github.com/YOUR_USERNAME/G90-SDR.git
git push -u origin main
```

**Users can then:**
```bash
git clone https://github.com/YOUR_USERNAME/G90-SDR.git
```

### Method 2: Archive Download

**Create release archive:**
```bash
cd ~
tar -czf G90-SDR-v1.0.tar.gz \
    --exclude='G90-SDR/venv' \
    --exclude='G90-SDR/logs/*.log' \
    --exclude='G90-SDR/__pycache__' \
    G90-SDR/
```

**Users download and extract:**
```bash
tar -xzf G90-SDR-v1.0.tar.gz
cd G90-SDR
```

### Method 3: Direct Sharing (USB, etc.)

Copy entire `G90-SDR/` directory to USB drive or share via file transfer.

---

## 📝 What to Include in Distribution

### Essential Files

```
G90-SDR/
├── README.md                 ← Project overview
├── INSTALL.md               ← Installation guide
├── LICENSE                  ← MIT License
├── requirements.txt         ← Python deps
├── install.bash            ← Installer
├── install_wrappers.bash   ← System integration
├── create_universal_launchers.bash
├── config/                  ← Config templates
├── scripts/                 ← All Python scripts
├── tests/                   ← Diagnostic tools
└── docs/                    ← Full documentation
```

### Do NOT Include

```
venv/                 # Virtual environment
logs/*.log            # Log files
__pycache__/          # Python cache
*.pyc                 # Compiled Python
config/audio_calibration.json  # User-specific
```

---

## 🌍 Sharing in the Ham Community

### Forums and Groups

**QRZ Forums:**
- Digital Modes section
- Software section
- Post with screenshots!

**Reddit:**
- r/amateurradio
- r/HamRadio
- r/RTLSDR

**Facebook Groups:**
- Xiegu G90 Users Group
- HF Digital Modes
- Amateur Radio Software

**QRZ.com:**
- Create project page
- Link to GitHub

### YouTube Demo

Create a video showing:
1. Installation process
2. Starting the system
3. Waterfall display in action
4. Tuning and changing frequencies
5. Digital mode operation

### Blog Post / Website

Write installation guide with:
- Screenshots
- Step-by-step instructions
- Troubleshooting tips
- Your operating experience

---

## 📸 What to Show

### Screenshots to Include

1. **Waterfall display** - GQRX showing active signals
2. **FlRig interface** - Connected to G90
3. **Frequency sync** - Show it following G90 changes
4. **Desktop launchers** - Easy access icons
5. **Diagnostic output** - Clean test results

### Demo Script

```
1. Show G90 with DE-19 connected
2. Click launcher icon
3. Watch FlRig start and connect
4. Watch GQRX start with waterfall
5. Change frequency on G90
6. Show GQRX following immediately
7. Tune to active frequency
8. Show waterfall displaying signals
```

---

## 💬 Support Strategy

### Documentation to Point Users To

1. **INSTALL.md** - Complete installation steps
2. **USER_GUIDE.md** - How to use the system
3. **TROUBLESHOOTING.md** - Common problems
4. **QUICK_REFERENCE.md** - Command cheat sheet

### Common Questions & Answers

**Q: Does this work on Raspberry Pi 4?**
A: Yes, but Pi 5 recommended for better performance.

**Q: Can I use a different radio?**
A: This is specifically for the G90, but could be adapted.

**Q: Do I need programming experience?**
A: No! Just follow the installation guide.

**Q: Does this transmit?**
A: No, receive only. FlRig controls the G90 for transmit.

**Q: What bands does it cover?**
A: All HF bands the G90 supports (160m-10m).

---

## 🐛 Issue Tracking

### Encourage Users to Report

**What you need from users:**
```bash
# Ask them to run and send results
cd $L_SDR_DIR
python3 tests/DiagnoseSystem.py > diagnostic.txt
cat diagnostic.txt
```

**Create GitHub Issues template:**
```markdown
## System Information
- OS: Ubuntu 24.04
- Hardware: Raspberry Pi 5
- G90-SDR Version: 1.0

## Problem Description
[Describe the issue]

## Diagnostic Output
```
[Paste output of DiagnoseSystem.py]
```

## Steps to Reproduce
1. 
2. 
3. 
```

---

## 🎉 Launch Checklist

Before sharing publicly:

- [ ] Test clean installation on fresh system
- [ ] Verify all documentation is complete
- [ ] Check all scripts have proper headers
- [ ] Ensure LICENSE file is included
- [ ] Test universal launchers work
- [ ] Verify diagnostic tools work
- [ ] Take quality screenshots
- [ ] Write clear README.md
- [ ] Create demo video (optional but recommended)
- [ ] Test on multiple desktop environments
- [ ] Have someone else test installation
- [ ] Set up GitHub repository
- [ ] Create first release tag (v1.0)

---

## 📢 Announcement Template

```
🎉 Introducing G90-SDR: Turn Your Xiegu G90 into a Full SDR!

I've created a complete software-defined radio system for the Xiegu G90 
that adds:
✅ Real-time waterfall display (GQRX)
✅ Full CAT control (FlRig)
✅ Automatic frequency synchronization
✅ Professional diagnostic tools
✅ Easy desktop launchers

Perfect for:
• Digital modes (FT8, PSK31, RTTY)
• Band monitoring
• DXing with visual waterfall
• Learning SDR technology

Tested on Raspberry Pi 5 with Ubuntu 24.04

GitHub: [your-link]
Documentation: Complete guides included
License: MIT (free and open source)

Works with:
• Xiegu G90 HF Transceiver
• Xiegu DE-19 Data Interface

Installation is automated - just run the installer!

Questions? Issues? Let me know!

73,
[Your Call Sign]
```

---

## 🎓 Educational Value

Emphasize learning opportunities:
- Understanding SDR technology
- Learning Python programming
- Linux system administration
- Digital signal processing basics
- Amateur radio digital modes

---

## 🤝 Community Contribution

Encourage others to:
- Report bugs
- Suggest features
- Contribute code
- Improve documentation
- Create tutorials
- Share their setups

---

## 📊 Success Metrics

Track:
- GitHub stars
- Downloads/clones
- Forum discussion threads
- YouTube video views
- User testimonials
- Bug reports (shows engagement!)

---

## 🎯 Your Mission Statement

*"Making SDR technology accessible to every Xiegu G90 owner, one installation at a time."*

**You're not just sharing code - you're empowering the ham community!**

73 and good DX! 📻✨

---

**Ready to share with the world?** 

The G90 community is going to love this! 🎉
