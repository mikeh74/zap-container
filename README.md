# ZAP Security Scanner

Flexible Docker-based setup for running OWASP ZAP security scans against multiple websites with organized, dated reports.

Now available as a **Python CLI tool** for easier installation and use!

## Features

- 🎯 Scan any website with a single command
- 📅 Automatically dated and organized reports
- 🗂️ Separate folders for each domain
- 📊 HTML index page for all scans
- 🔧 Customizable scan configurations per domain
- 📝 Multiple report formats (HTML, Markdown, JSON)
- 🐍 **NEW:** Python CLI with Click framework
- 🌐 **NEW:** Built-in HTTP server for viewing reports
- ✨ **NEW:** Pre-commit hooks for code quality

## Installation

### Option 1: Install as Python Package (Recommended)

```bash
# Clone the repository
git clone https://github.com/mikeh74/zap-container.git
cd zap-container

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Option 2: Use Shell Scripts (Traditional)

The original shell scripts are still available for direct use:

```bash
chmod +x scan.sh generate-index.sh scan-batch.sh
```

## Quick Start

### Python CLI (Recommended)

```bash
# Run a baseline scan
zap-scan scan https://www.example.com

# Run a full scan (more thorough)
zap-scan scan https://www.example.com --scan-type full

# Generate the index page
zap-scan generate-index

# Serve reports in browser
zap-scan serve
```

### Shell Scripts (Traditional)

```bash
# Run a baseline scan
./scan.sh https://www.example.com

# Run a full scan (more thorough)
./scan.sh https://www.example.com full

# Generate the index page
./generate-index.sh
```

## Python CLI Commands

### `zap-scan scan`

Run a ZAP security scan on a target URL.

```bash
# Basic baseline scan
zap-scan scan https://www.example.com

# Full active scan
zap-scan scan https://www.example.com --scan-type full

# API scan (requires config)
zap-scan scan https://api.example.com --scan-type api

# Use custom directories
zap-scan scan https://www.example.com --reports-dir my-reports --configs-dir my-configs
```

### `zap-scan batch`

Run batch scans on multiple targets from a config file.

Config files can be in either plain text (.txt) or YAML (.yaml/.yml) format:

**Text format (.txt):**
```txt
https://www.example.com
https://www.example.com baseline
https://api.example.com full
```

**YAML format (.yaml):**
```yaml
targets:
  - url: https://www.example.com
    scan_type: baseline
  - url: https://api.example.com
    scan_type: full
```

The YAML format allows for future extensibility with additional options per target.

```bash
# Scan targets from default file (targets.txt)
zap-scan batch

# Scan targets from YAML file
zap-scan batch --config targets.yaml

# Scan targets from custom file
zap-scan batch --config my-targets.txt

# Use custom delay between scans
zap-scan batch --delay 10
```

### `zap-scan generate-index`

Generate an HTML index page for all scan reports.

```bash
# Generate index with default reports directory
zap-scan generate-index

# Generate index for custom reports directory
zap-scan generate-index --reports-dir my-reports
```

### `zap-scan serve`

Start an HTTP server to view reports in a browser.

```bash
# Serve reports on default port (8000)
zap-scan serve

# Serve reports on custom port
zap-scan serve --port 8080

# Serve custom reports directory
zap-scan serve --reports-dir my-reports
```

Then open http://localhost:8000/index.html in your browser.

## Directory Structure

After running scans, your directory will look like this:

```
├── pyproject.toml               # Python package configuration
├── .pre-commit-config.yaml      # Pre-commit hooks configuration
├── zap_scan/                    # Python package source
│   ├── __init__.py
│   ├── cli.py                  # CLI commands
│   ├── scanner.py              # Core scanning logic
│   ├── batch.py                # Batch scanning
│   ├── index_generator.py      # HTML index generation
│   └── server.py               # HTTP server
├── scan.sh                      # Shell script (legacy)
├── scan-batch.sh               # Shell script (legacy)
├── generate-index.sh            # Shell script (legacy)
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

## Usage with Python CLI

### Basic Scanning

```bash
# Baseline scan (quick, passive + spider)
zap-scan scan https://www.example.com

# Full scan (includes active scanning)
zap-scan scan https://www.example.com --scan-type full

# API scan (requires config file)
zap-scan scan https://api.example.com --scan-type api
```

### Basic Scanning (Shell Scripts)

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

Add to crontab for automated scanning (using Python CLI):

```bash
# Scan every day at 2 AM
0 2 * * * cd /path/to/zap && zap-scan scan https://www.example.com && zap-scan generate-index
```

Or with shell scripts:

```bash
# Scan every day at 2 AM
0 2 * * * cd /path/to/zap && ./scan.sh https://www.example.com && ./generate-index.sh
```

### CI/CD Integration

GitHub Actions example using Python CLI:

```yaml
# GitHub Actions example
- name: Install ZAP Scan CLI
  run: |
    pip install -e .

- name: Run ZAP Scan
  run: |
    zap-scan scan https://staging.example.com

- name: Upload Reports
  uses: actions/upload-artifact@v3
  with:
    name: zap-reports
    path: reports/
```

Or using shell scripts:

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

Using Python CLI with batch command:

**Using plain text format (.txt):**

```bash
# Create targets.txt with your URLs
cat > targets.txt << EOF
https://www.example.com
https://api.example.com full
https://admin.example.com
EOF

# Run batch scan
zap-scan batch
```

**Using YAML format (.yaml) - Recommended:**

```bash
# Create targets.yaml with structured config
cat > targets.yaml << EOF
targets:
  - url: https://www.example.com
    scan_type: baseline
  - url: https://api.example.com
    scan_type: full
  - url: https://admin.example.com
    scan_type: baseline
EOF

# Run batch scan
zap-scan batch --config targets.yaml
```

The YAML format is recommended as it allows for future extensibility with additional options like credentials, custom configurations, and exclusion patterns.
```

Or using shell script:

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

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/mikeh74/zap-container.git
cd zap-container

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Pre-commit Hooks

This project uses pre-commit hooks to maintain code quality:

- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Code linting
- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml**: Validate YAML files
- **check-toml**: Validate TOML files

```bash
# Run pre-commit on all files
pre-commit run --all-files

# Run pre-commit on staged files (automatic on commit)
git commit
```

### Code Style

The project follows these conventions:

- **Line length**: 100 characters
- **Formatter**: Black
- **Import sorting**: isort with Black profile
- **Type hints**: Encouraged but not required

### Running Linters Manually

```bash
# Format code with black
black zap_scan/

# Sort imports
isort zap_scan/

# Check with flake8
flake8 zap_scan/ --max-line-length=100 --extend-ignore=E203,W503,W293,E501
```

### Publishing to PyPI (Future)

When ready to publish to PyPI:

```bash
# Build package
python -m build

# Upload to PyPI (requires credentials)
python -m twine upload dist/*
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
