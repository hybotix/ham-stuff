# G90-SDR Environment Variables

Complete guide to environment variables for multi-environment workflows.

---

## 📋 Overview

G90-SDR uses environment variables to support multiple installation configurations:
- **Production** - Stable, working installation
- **Testing** - Experimental features, new versions
- **Development** - Active development, breaking changes

---

## 🎯 Environment Variables

### **G90_SDR_DIR** (Canonical/Production)

**Purpose:** Points to the **production** G90-SDR installation

**Usage:** This should always point to your stable, working installation

**Example:**
```bash
export G90_SDR_DIR=$HOME/Virtual/G90-SDR
```

**Priority:** Checked **FIRST** by all wrapper scripts

**When to use:**
- Your main, stable installation
- What you use for actual radio operation
- Always keeps working while you test elsewhere

---

### **L_SDR_DIR** (Local/Active)

**Purpose:** Points to the **currently active** installation (may override production)

**Usage:** Use this for testing new versions or features

**Example:**
```bash
export L_SDR_DIR=$HOME/Virtual/G90-SDR-test
```

**Priority:** Checked **SECOND** (after G90_SDR_DIR)

**When to use:**
- Testing new features
- Trying beta versions
- Development work
- Temporary installations

---

### **L_VIRT_DIR** (Virtual Directory Base)

**Purpose:** Base directory for all virtual/project directories

**Usage:** Organizational convenience for multiple projects

**Example:**
```bash
export L_VIRT_DIR=$HOME/Virtual
```

**When to use:**
- You have multiple projects in ~/Virtual/
- Want consistent organization
- Easy to reference in other scripts

---

## 🔄 Search Priority

When wrappers look for G90-SDR, they check in this order:

```
1. $G90_SDR_DIR              ← Production (if set and valid)
2. $L_SDR_DIR                ← Active/Testing (if set and valid)
3. $HOME/Virtual/G90-SDR     ← Default location
4. $HOME/G90-SDR             ← Alternative location
5. $HOME/Documents/G90-SDR   ← Documents folder
6. /opt/G90-SDR              ← System-wide install
7. /usr/local/share/G90-SDR  ← Alternative system location
```

---

## 💼 Common Configurations

### **Configuration 1: Single Installation**

Most users - one installation, simple setup:

```bash
# In ~/.bashrc
export L_VIRT_DIR=$HOME/Virtual
export L_SDR_DIR=$L_VIRT_DIR/G90-SDR
export G90_SDR_DIR=$L_SDR_DIR
```

**Result:** Both point to same location, everything simple

---

### **Configuration 2: Production + Testing**

Power users - stable production, separate testing:

```bash
# In ~/.bashrc
export L_VIRT_DIR=$HOME/Virtual

# Production (stable)
export G90_SDR_DIR=$L_VIRT_DIR/G90-SDR

# Testing (experimental)
export L_SDR_DIR=$L_VIRT_DIR/G90-SDR-test
```

**Result:** 
- `g90-sdr` uses testing version (L_SDR_DIR takes priority)
- Production remains untouched
- Can switch by changing L_SDR_DIR

---

### **Configuration 3: Multiple Versions**

Developers - multiple installations for different purposes:

```bash
# In ~/.bashrc
export L_VIRT_DIR=$HOME/Virtual

# Production
export G90_SDR_DIR=$L_VIRT_DIR/G90-SDR

# Development (default)
export L_SDR_DIR=$L_VIRT_DIR/G90-SDR-dev

# Also available (manually switch):
# export L_SDR_DIR=$L_VIRT_DIR/G90-SDR-beta
# export L_SDR_DIR=$L_VIRT_DIR/G90-SDR-experimental
```

**Result:** Quick switching between versions

---

## 🔀 Switching Environments

### **Temporarily Switch to Production**

```bash
# Override L_SDR_DIR for one command
G90_SDR_DIR=$HOME/Virtual/G90-SDR L_SDR_DIR= g90-sdr
```

### **Temporarily Switch to Testing**

```bash
# Override both for one command
export L_SDR_DIR=$HOME/Virtual/G90-SDR-test
g90-sdr
```

### **Permanently Switch Active Installation**

```bash
# Edit ~/.bashrc
nano ~/.bashrc

# Change:
export L_SDR_DIR=$L_VIRT_DIR/G90-SDR-test

# Reload
source ~/.bashrc
```

---

## 🧪 Testing Workflow Example

### **Setup:**

```bash
# Production (always stable)
export G90_SDR_DIR=$HOME/Virtual/G90-SDR

# Testing (what you're currently working on)
export L_SDR_DIR=$HOME/Virtual/G90-SDR-test

# Working directory
export L_VIRT_DIR=$HOME/Virtual
```

### **Workflow:**

```bash
# 1. Install production
cd $L_VIRT_DIR
git clone <repo> G90-SDR
cd G90-SDR
bash install.bash

# 2. Create test copy
cp -r G90-SDR G90-SDR-test

# 3. Test new features in test copy
cd G90-SDR-test
# Make changes, test features
bash utils/rebuild_all.bash  # Build latest versions

# 4. Run test version
g90-sdr  # Uses G90-SDR-test (L_SDR_DIR)

# 5. If test version works, promote to production
cd $L_VIRT_DIR
rm -rf G90-SDR
mv G90-SDR-test G90-SDR

# 6. Reset L_SDR_DIR to production
export L_SDR_DIR=$G90_SDR_DIR
```

---

## 📊 Variable Comparison

| Variable | Purpose | Priority | Typical Use |
|----------|---------|----------|-------------|
| G90_SDR_DIR | Production/Canonical | 1st | Stable installation |
| L_SDR_DIR | Active/Testing | 2nd | Current work |
| L_VIRT_DIR | Base directory | N/A | Organization |

---

## 🎯 Best Practices

### **For Most Users:**

```bash
# Simple - both point to same place
export L_SDR_DIR=$HOME/Virtual/G90-SDR
export G90_SDR_DIR=$L_SDR_DIR
```

### **For Developers:**

```bash
# Production stays stable
export G90_SDR_DIR=$HOME/Virtual/G90-SDR

# Testing is separate and changeable
export L_SDR_DIR=$HOME/Virtual/G90-SDR-dev
```

### **For System Administrators:**

```bash
# System-wide production
export G90_SDR_DIR=/opt/G90-SDR

# User-specific testing
export L_SDR_DIR=$HOME/G90-SDR-test
```

---

## 🔍 Checking Current Configuration

### **See What's Set:**

```bash
echo "G90_SDR_DIR: $G90_SDR_DIR"
echo "L_SDR_DIR:   $L_SDR_DIR"
echo "L_VIRT_DIR:  $L_VIRT_DIR"
```

### **See Which Will Be Used:**

```bash
g90-sdr --find
```

### **Test Configuration:**

```bash
# Check production
ls -la $G90_SDR_DIR

# Check active
ls -la $L_SDR_DIR

# See if they differ
if [ "$G90_SDR_DIR" = "$L_SDR_DIR" ]; then
    echo "Same installation"
else
    echo "Different installations:"
    echo "  Production: $G90_SDR_DIR"
    echo "  Active:     $L_SDR_DIR"
fi
```

---

## 🐛 Troubleshooting

### **Problem: Which installation is running?**

```bash
g90-sdr --find
# Shows exactly which directory will be used
```

### **Problem: Changes not taking effect**

```bash
# Ensure you reloaded .bashrc
source ~/.bashrc

# Or start new terminal session
```

### **Problem: Want to ignore environment variables**

```bash
# Unset temporarily
unset G90_SDR_DIR L_SDR_DIR

# Run command
g90-sdr
# Will use default search order
```

---

## 📝 .bashrc Template

Complete template for your `.bashrc`:

```bash
# ============================================================================
# G90-SDR Environment Variables
# ============================================================================

# Base directory for virtual environments/projects
export L_VIRT_DIR=$HOME/Virtual

# Production G90-SDR (stable, always works)
export G90_SDR_DIR=$L_VIRT_DIR/G90-SDR

# Active G90-SDR (current working version)
# Option 1: Same as production (most users)
export L_SDR_DIR=$G90_SDR_DIR

# Option 2: Separate testing installation (developers)
# export L_SDR_DIR=$L_VIRT_DIR/G90-SDR-test

# Option 3: Development installation
# export L_SDR_DIR=$L_VIRT_DIR/G90-SDR-dev

# ============================================================================
```

---

## 🎓 Understanding the "L_" Prefix

**"L_" = LOCAL**

Meaning:
- User-specific (not system-wide)
- Local to your account
- Configurable per user
- Not shared across users

**Why this naming?**
- Clear indication it's a local/user variable
- Distinguishes from system variables
- Consistent naming pattern
- Easy to remember

---

## 🚀 Advanced: Switching Scripts

### **Create Quick Switcher:**

```bash
# Filename: ~/bin/switch-sdr
#!/bin/bash

case "$1" in
    prod)
        export L_SDR_DIR=$G90_SDR_DIR
        echo "Switched to production"
        ;;
    test)
        export L_SDR_DIR=$HOME/Virtual/G90-SDR-test
        echo "Switched to testing"
        ;;
    dev)
        export L_SDR_DIR=$HOME/Virtual/G90-SDR-dev
        echo "Switched to development"
        ;;
    *)
        echo "Usage: switch-sdr {prod|test|dev}"
        ;;
esac
```

---

## 📚 Summary

**Simple Setup (Most Users):**
```bash
export L_SDR_DIR=$HOME/Virtual/G90-SDR
export G90_SDR_DIR=$L_SDR_DIR
```

**Advanced Setup (Developers):**
```bash
export G90_SDR_DIR=$HOME/Virtual/G90-SDR      # Production
export L_SDR_DIR=$HOME/Virtual/G90-SDR-test   # Testing
```

**The system automatically finds the right installation based on your environment variables!**

---

**Your multi-environment workflow is now fully supported!** 🎉
