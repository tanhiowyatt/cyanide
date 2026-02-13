# Data Paths Documentation

This document explains the purpose and structure of the static data directories used by Cyanide Honeypot.

## `fs_yaml` (Filesystem Configuration)

**Configuration Key:** `fs_yaml` (cfg)  
**Default Path:** `config/fs-config/fs.ubuntu_22_04.yaml` (if no `fs_yaml` is specified and `os_profile` is `ubuntu_22_04`)

### Purpose
Defines the virtual filesystem template and OS metadata. Each profile has its own YAML file.

### Directory Structure: `config/fs-config/`
- `fs.ubuntu_22_04.yaml`: Ubuntu 22.04 LTS profile.
- `fs.debian_11.yaml`: Debian 11 profile.
- `fs.centos_7.yaml`: CentOS 7 profile.
- `fs.yaml.example`: Template for creating new filesystems.

### How to Customize
1. **Edit the profile YAML:**
   ```bash
   nano config/fs-config/fs.ubuntu_22_04.yaml
   ```
2. **Customize Metadata:**
   Edit the `metadata:` section at the top of the file to change SSH banners or kernel versions.
3. **Restart honeypot:**
   ```bash
   docker compose -f docker/docker-compose.yml restart cyanide
   ```

## `var/` (Persistent Data)
- **`var/log/cyanide/`**: JSON logs and TTY session recordings.
- **`var/lib/cyanide/quarantine/`**: Isolated files captured from attackers.
