# ZAP Security Scanner

Flexible Docker-based setup for running OWASP ZAP security scans against multiple websites with organized, dated reports.

## Features

- 🎯 Scan any website with a single command
- 📅 Automatically dated and organized reports
- 🗂️ Separate folders for each domain
- 📊 HTML index page for all scans
- 🔧 Customizable scan configurations per domain
- 📝 Multiple report formats (HTML, Markdown, JSON)

## Quick Start

### 1. Run a Quick Scan

```bash
# Make scripts executable (first time only)
chmod +x scan.sh generate-index.sh

# Run a baseline scan
./scan.sh https://www.example.com

# Run a full scan (more thorough)
./scan.sh https://www.example.com full
```

### 2. View Reports

```bash
# Generate the index page
./generate-index.sh

# Open in browser (macOS)
open reports/index.html

# Or (Linux)
xdg-open reports/index.html
```

## Directory Structure

After running scans, your directory will look like this:

```
├── scan.sh                      # Main scan script
├── generate-index.sh            # Index generator
├── configs/                     # Configuration files
│   ├── zap-template.yaml       # Template for custom configs
│   └── <domain>/               # Domain-specific configs
│       └── zap.yaml
├── reports/                     # All scan reports
│   ├── index.html              # Main index page
│   └── <domain>/               # Reports organized by domain
│       └── YYYY-MM-DD/         # Reports organized by date
│           ├── scan_YYYYMMDD_HHMMSS.html
│           ├── scan_YYYYMMDD_HHMMSS.md
│           └── scan_YYYYMMDD_HHMMSS.json
└── compose.yml                  # Docker Compose (alternative method)
```

## Usage

### Basic Scanning

```bash
# Baseline scan (quick, passive + spider)
./scan.sh https://www.example.com

# Full scan (includes active scanning)
./scan.sh https://www.example.com full

# API scan (requires config file)
./scan.sh https://api.example.com api
```

### Custom Configuration

1. Create a config directory for your domain:
```bash
mkdir -p configs/www_example_com
```

2. Copy and edit the template:
```bash
cp configs/zap-template.yaml configs/www_example_com/zap.yaml
# Edit configs/www_example_com/zap.yaml with your settings
```

3. Run scan (will automatically use the config):
```bash
./scan.sh https://www.example.com
```

### Configuration Options

Edit `configs/<domain>/zap.yaml` to customize:

- **URLs to scan**: Target URLs and scope
- **Exclude paths**: Logout, admin areas, etc.
- **Spider settings**: Max duration, depth, children
- **Scan types**: Enable/disable active scanning
- **Authentication**: Configure login if needed
- **Alert thresholds**: Customize what gets reported

See [configs/zap-template.yaml](configs/zap-template.yaml) for full options.

## Report Index

The `generate-index.sh` script creates a beautiful HTML dashboard showing:

- 📊 Statistics (total scans, domains tested, last scan time)
- 🗂️ Reports organized by domain
- 📅 Reports organized by date
- 🔗 Quick links to HTML, Markdown, and JSON reports
- 📱 Responsive design for mobile viewing

## Using Docker Compose (Alternative)

You can also use Docker Compose directly:

```bash
# Set environment variables
export TARGET_URL="https://www.example.com"
export REPORT_DIR="./reports/example_com/$(date +%Y-%m-%d)"
export REPORT_HTML="scan_$(date +%Y%m%d_%H%M%S).html"
export REPORT_MD="scan_$(date +%Y%m%d_%H%M%S).md"
export REPORT_JSON="scan_$(date +%Y%m%d_%H%M%S).json"

# Create directory
mkdir -p "$REPORT_DIR"

# Run scan
docker-compose up
```

## Scan Types

### Baseline Scan (Default)
- Quick passive scan
- Spiders the website
- No active attacks
- Safe for production sites
- Takes 5-15 minutes

### Full Scan
- Everything in baseline
- Plus active scanning
- Tests for vulnerabilities
- May trigger security alerts
- Takes 30+ minutes

### API Scan
- Designed for REST APIs
- Requires OpenAPI/Swagger spec
- Can test API endpoints
- Requires custom config

## Troubleshooting

### Permission Denied
```bash
chmod +x scan.sh generate-index.sh
```

### Docker Not Running
```bash
# macOS/Linux
docker ps
# Start Docker Desktop if needed
```

### No Reports Generated
- Check that the scan completed successfully
- Look for error messages in terminal output
- Verify target URL is accessible
- Check Docker logs: `docker logs <container-id>`

### Reports Not Showing in Index
```bash
# Regenerate index
./generate-index.sh
```

## Advanced Usage

### Scheduled Scans

Add to crontab for automated scanning:

```bash
# Scan every day at 2 AM
0 2 * * * cd /path/to/zap && ./scan.sh https://www.example.com && ./generate-index.sh
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run ZAP Scan
  run: |
    chmod +x scan.sh
    ./scan.sh https://staging.example.com
    
- name: Upload Reports
  uses: actions/upload-artifact@v3
  with:
    name: zap-reports
    path: reports/
```

### Multiple Targets

```bash
#!/bin/bash
# scan-all.sh - Scan multiple sites

TARGETS=(
    "https://www.example.com"
    "https://api.example.com"
    "https://admin.example.com"
)

for target in "${TARGETS[@]}"; do
    echo "Scanning $target..."
    ./scan.sh "$target"
done

./generate-index.sh
echo "All scans complete!"
```

## Resources

- [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)
- [ZAP Automation Framework](https://www.zaproxy.org/docs/automate/automation-framework/)
- [ZAP Docker Images](https://www.zaproxy.org/docs/docker/)

## Security Notes

- **Baseline scans** are safe for production sites
- **Full scans** may trigger security alerts or WAFs
- Always get permission before scanning
- Use authentication configs for protected areas
- Exclude sensitive endpoints (logout, delete, etc.)

## License

This setup is provided as-is for security testing purposes. Always obtain proper
authorization before scanning any website.

## Additional Resources

### Scan Types 

You can read more about the scane types here:
* [Baseline](https://www.zaproxy.org/docs/docker/baseline-scan/)
* [Full Scan](https://www.zaproxy.org/docs/docker/full-scan/)

### Webswing

You can run the full ZAP GUI using webswing, docs here:
<https://www.zaproxy.org/docs/docker/webswing/>

Example:
```
docker run -u zap -p 8080:8080 -p 8090:8090 -i owasp/zap2docker-stable zap-webswing.sh
```