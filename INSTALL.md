# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Docker (for running ZAP scans)
- pip (Python package manager)

## Installation Methods

### Method 1: Install from Source (Development)

If you want to contribute or modify the code:

```bash
# Clone the repository
git clone https://github.com/mikeh74/zap-container.git
cd zap-container

# Install in editable mode
pip install -e .

# Verify installation
zap-scan --version
```

### Method 2: Install with Development Tools

If you want to contribute and use pre-commit hooks:

```bash
# Clone the repository
git clone https://github.com/mikeh74/zap-container.git
cd zap-container

# Install with development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Verify installation
zap-scan --version
```

### Method 3: Install from PyPI (Future)

Once published to PyPI, you'll be able to install with:

```bash
pip install zap-scan
```

## Quick Start

After installation, run your first scan:

```bash
# Run a baseline scan
zap-scan scan https://www.example.com

# Generate index page
zap-scan generate-index

# Serve reports in browser
zap-scan serve
```

Then open http://localhost:8000/index.html in your browser to view the reports.

## Verify Docker is Running

ZAP scans require Docker to be running:

```bash
# Check Docker status
docker ps

# If Docker is not running, start Docker Desktop or Docker service
```

## Configuration

### Custom Scan Configuration

To use custom ZAP configurations:

1. Create a domain-specific config directory:
   ```bash
   mkdir -p configs/www_example_com
   ```

2. Copy the template:
   ```bash
   cp configs/zap-template.yaml configs/www_example_com/zap.yaml
   ```

3. Edit the config file with your settings

4. Run the scan (config will be auto-detected):
   ```bash
   zap-scan scan https://www.example.com
   ```

### Batch Scanning

Create a `targets.txt` file with URLs to scan:

```
https://www.example.com
https://api.example.com full
https://app.example.com
```

Then run:

```bash
zap-scan batch
```

## Troubleshooting

### Command not found

If you get "command not found" after installation:

```bash
# Try running with python -m
python -m zap_scan.cli --version

# Or add pip's bin directory to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Docker permission denied

On Linux, you may need to add your user to the docker group:

```bash
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### ModuleNotFoundError

If you get module import errors:

```bash
# Reinstall the package
pip uninstall zap-scan
pip install -e .
```

## Uninstallation

To uninstall:

```bash
pip uninstall zap-scan
```

## Next Steps

- Read the [README.md](README.md) for detailed usage instructions
- Check out the [Quick Start Guide](QUICKSTART.md)
- Explore the example configurations in `configs/zap-template.yaml`
