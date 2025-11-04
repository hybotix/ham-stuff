# G90-SDR Naming Conventions

This document describes the file naming standards used in the G90-SDR project.

---

## File Extensions by Type

### Shell Scripts: `.bash`
All bash shell scripts use the `.bash` extension to explicitly show the shell being used.

**Examples:**
- `install.bash`
- `update.bash`
- `check_env.bash`
- `fix_permissions.bash`

**Rationale:** Makes it immediately clear that these are bash scripts, not generic shell scripts that might work with sh, zsh, etc.

### Python Scripts: `.py`
All Python scripts use the standard `.py` extension.

**Examples:**
- `rig_control.py`
- `frequency_sync.py`
- `TestConnection.py`

### Documentation: `.md`
All documentation uses Markdown format with `.md` extension.

**Examples:**
- `README.md`
- `USER_GUIDE.md`
- `TROUBLESHOOTING.md`

---

## Python File Naming

### Regular Modules: `lowercase_with_underscores.py`
Standard Python modules follow PEP 8 naming conventions.

**Examples:**
- `rig_control.py`
- `frequency_sync.py`
- `audio_router.py`
- `config_manager.py`

### Test Scripts: `CapitalizedWords.py`
Test and diagnostic scripts use capital letters for each word (PascalCase).

**Examples:**
- `TestConnection.py`
- `TestAudio.py`
- `TestCatControl.py`
- `DiagnoseSystem.py`
- `CalibrateAudio.py`

**Rationale:** Makes test scripts easily identifiable and distinguishable from regular modules.

---

## Bash Script Naming

### Standard Scripts: `lowercase_words.bash`
Most bash scripts use lowercase with underscores.

**Examples:**
- `install.bash`
- `update.bash`
- `check_env.bash`
- `fix_all.bash`

### Special Cases: `action_target.bash`
Scripts that perform an action on a target use underscore separation.

**Examples:**
- `make_executable.bash` (make what executable)
- `fix_permissions.bash` (fix what permissions)
- `create_all_files.bash` (create what files)

---

## Directory Naming

All directories use lowercase names:

```
scripts/     # Main application scripts
tests/       # Test and diagnostic scripts
config/      # Configuration files
docs/        # Documentation
logs/        # Log files
```

---

## Configuration File Naming

### YAML: `descriptive_name.yaml`
Configuration files use descriptive lowercase names.

**Example:**
- `g90_sdr.yaml`

### XML: `application_config.xml`
XML configuration files follow same pattern.

**Example:**
- `flrig_g90.xml`

### INI/CONF: `descriptive.conf`
Generic config files use `.conf` extension.

**Example:**
- `gqrx_config.conf`
- `audio_routing.conf`

---

## Documentation Naming

### Major Docs: `UPPERCASE.md`
Important top-level documentation uses all caps.

**Examples:**
- `README.md`
- `INSTALL.md`
- `LICENSE`

### Detailed Guides: `CAPITALIZED_WORDS.md`
Detailed guides use capitalized words with underscores.

**Examples:**
- `USER_GUIDE.md`
- `TROUBLESHOOTING.md`
- `PROJECT_STRUCTURE.md`
- `QUICK_REFERENCE.md`

---

## Special Files

### Python Requirements: `requirements.txt`
Standard Python convention for dependency lists.

### Git Ignore: `.gitignore`
Standard git configuration file.

### Environment Check: `check_env.bash`
Uses descriptive verb + noun pattern.

---

## Shebang Lines

### Bash Scripts
```bash
#!/bin/bash
```

**Note:** Uses `/bin/bash` explicitly (not `/bin/sh` or `/usr/bin/env bash`)

### Python Scripts
```python
#!/usr/bin/env python3
```

**Note:** Uses `env` to find Python 3 in the PATH

---

## Environment Variables

### Project Directory: `L_SDR_DIR`
Points to the G90-SDR installation directory.

**Setting:**
```bash
export L_SDR_DIR=$HOME/Virtual/G90-SDR
```

**Usage in bash:**
```bash
if [ -n "$L_SDR_DIR" ]; then
    cd "$L_SDR_DIR"
fi
```

**Usage in Python:**
```python
import os
if 'L_SDR_DIR' in os.environ:
    project_dir = os.environ['L_SDR_DIR']
```

---

## File Permission Standards

### Executable Scripts
All `.bash` and `.py` files should be executable:
```bash
-rwxr-xr-x  # 755 permissions
```

### Configuration Files
Config files should be readable but not executable:
```bash
-rw-r--r--  # 644 permissions
```

### Documentation
Documentation files should be readable:
```bash
-rw-r--r--  # 644 permissions
```

---

## Summary Table

| Type | Extension | Naming | Example |
|------|-----------|--------|---------|
| Bash script | `.bash` | lowercase_words | `install.bash` |
| Python module | `.py` | lowercase_words | `rig_control.py` |
| Python test | `.py` | CapitalWords | `TestConnection.py` |
| Config YAML | `.yaml` | lowercase_words | `g90_sdr.yaml` |
| Config other | `.conf`, `.xml` | lowercase_words | `audio_routing.conf` |
| Major docs | `.md` | UPPERCASE | `README.md` |
| Guide docs | `.md` | UPPER_WORDS | `USER_GUIDE.md` |
| Requirements | `.txt` | lowercase | `requirements.txt` |

---

## Benefits of This Convention

1. **Clarity**: File extensions show exactly what shell/language is used
2. **Organization**: Naming patterns group related files
3. **Portability**: `$L_SDR_DIR` allows easy relocation
4. **Consistency**: All files follow predictable patterns
5. **Maintainability**: Easy to find and identify file types

---

## Future Conventions

If adding new file types:

- **Perl scripts**: Use `.perl` extension
- **Shell scripts**: Use `.sh` only for POSIX sh
- **Zsh scripts**: Use `.zsh` extension
- **Fish scripts**: Use `.fish` extension

This maintains the pattern of explicit shell identification.

---

**Remember:** When you relocate the project, just change `$L_SDR_DIR` in your `.bashrc` and everything continues to work!
