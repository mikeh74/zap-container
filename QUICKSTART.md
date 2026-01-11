# ZAP Setup - Quick Reference

## 🚀 Quick Start

```bash
# 1. Run a scan
./scan.sh https://www.example.com

# 2. Generate index
./generate-index.sh

# 3. View reports
open reports/index.html
```

## 📁 New Structure

```
zap/
├── scan.sh              # Main scan script
├── generate-index.sh    # Generate HTML index
├── scan-batch.sh        # Scan multiple sites
├── migrate-reports.sh   # Migrate old reports
├── targets.txt          # Batch scan targets (text format)
├── targets.yaml         # Batch scan targets (YAML format, recommended)
├── configs/
│   ├── zap-template.yaml
│   └── <domain>/zap.yaml
└── reports/
    ├── index.html       # Main dashboard
    └── <domain>/
        └── YYYY-MM-DD/
            ├── *.html
            ├── *.md
            └── *.json
```

## 📝 Common Commands

### Single Site Scan
```bash
# Quick baseline scan
./scan.sh https://www.example.com

# Full scan with active attacks
./scan.sh https://www.example.com full

# API scan (requires config)
./scan.sh https://api.example.com api
```

### Batch Scanning
```bash
# Edit targets.txt or targets.yaml first
# Text format (targets.txt):
#   https://www.example.com
#   https://api.example.com full

# YAML format (targets.yaml) - Recommended for more options:
#   targets:
#     - url: https://www.example.com
#       scan_type: baseline
#     - url: https://api.example.com
#       scan_type: full

# Run batch scan with shell script (text format only)
./scan-batch.sh

# Or use a different text file:
./scan-batch.sh my-sites.txt

# For YAML format, use Python CLI:
zap-scan batch --config targets.yaml
```

### Migrate Old Reports
```bash
# Move old reports to new structure
./migrate-reports.sh

# Then regenerate index
./generate-index.sh
```

### Custom Configuration
```bash
# 1. Create config directory
mkdir -p configs/www_example_com

# 2. Copy template
cp configs/zap-template.yaml configs/www_example_com/zap.yaml

# 3. Edit the config
nano configs/www_example_com/zap.yaml

# 4. Run scan (automatically uses config)
./scan.sh https://www.example.com
```

## 🎯 Scan Types

| Type | Duration | Description | Use Case |
|------|----------|-------------|----------|
| **baseline** | 5-15 min | Passive + Spider | Production sites |
| **full** | 30+ min | Active scanning | Staging/Testing |
| **api** | 10-20 min | API-specific | REST APIs |

## 📊 Index Page Features

- Total scan statistics
- Domain organization
- Date-based grouping
- Multiple report formats
- Responsive design
- Direct report links

## 🔧 Configuration Options

Edit `configs/<domain>/zap.yaml`:

- **URLs**: Target and scope
- **Exclusions**: Logout, admin paths
- **Spider**: Duration, depth, children
- **Authentication**: Login handling
- **Active Scan**: Enable/disable
- **Alerts**: Thresholds and rules

## 🔄 Scheduled Scans

### Cron Example
```bash
# Daily at 2 AM
0 2 * * * cd /path/to/zap && ./scan-batch.sh && ./generate-index.sh
```

### GitHub Actions
```yaml
- name: Security Scan
  run: |
    ./scan.sh https://staging.example.com
    ./generate-index.sh

- name: Upload Reports
  uses: actions/upload-artifact@v3
  with:
    name: zap-reports
    path: reports/
```

## 🐛 Troubleshooting

### Permission Issues
```bash
chmod +x *.sh
```

### Docker Not Running
```bash
docker ps
```

### Reports Not Generated
- Check terminal output for errors
- Verify target URL is accessible
- Check Docker logs
- Ensure sufficient disk space

### Missing from Index
```bash
./generate-index.sh
```

## 📖 File Descriptions

| File | Purpose |
|------|---------|
| `scan.sh` | Main scanning script |
| `generate-index.sh` | Create HTML index |
| `scan-batch.sh` | Multiple site scanning |
| `migrate-reports.sh` | Move old reports |
| `targets.txt` | Batch scan list (text format) |
| `targets.yaml` | Batch scan list (YAML format, recommended) |
| `compose.yml` | Docker Compose config |
| `configs/zap-template.yaml` | Config template |

## 🔐 Security Notes

- Get permission before scanning
- Baseline scans are production-safe
- Full scans may trigger alerts
- Exclude sensitive endpoints
- Use authentication configs carefully

## 📚 Resources

- [ZAP Documentation](https://www.zaproxy.org/docs/)
- [Automation Framework](https://www.zaproxy.org/docs/automate/automation-framework/)
- [Docker Images](https://www.zaproxy.org/docs/docker/)

## 💡 Tips

1. Start with baseline scans
2. Create custom configs for important sites
3. Schedule regular scans
4. Review reports regularly
5. Update exclusion lists as needed
6. Keep ZAP Docker image updated: `docker pull ghcr.io/zaproxy/zaproxy:stable`
