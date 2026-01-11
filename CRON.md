# Running ZAP Scans with Cron

This guide explains how to set up automated security scans using cron for regular scanning of your domains.

## Overview

The `zap-scan batch` CLI command is well-suited for automated cron jobs because it:
- Runs self-contained executions
- Returns proper exit codes (0=success, 1=warnings, 2=failures)
- Automatically generates reports and index pages
- Handles multiple targets with configurable delays

## Quick Start

### Basic Cron Setup

Add to your crontab (`crontab -e`):

```cron
# Daily scan at 2 AM
0 2 * * * /usr/local/bin/zap-scan batch --config /path/to/targets.txt

# Weekly full scan on Sunday at 3 AM
0 3 * * 0 /usr/local/bin/zap-scan batch --config /path/to/weekly-targets.txt --delay 15
```

## Production Cron Wrapper Script

For production use, create a wrapper script with logging, error handling, and alerting:

```bash
#!/bin/bash
# /usr/local/bin/zap-cron-scan.sh

set -euo pipefail

# Configuration
TARGETS_FILE="${TARGETS_FILE:-/opt/zap-scanner/targets.txt}"
REPORTS_DIR="${REPORTS_DIR:-/opt/zap-scanner/reports}"
LOG_DIR="${LOG_DIR:-/var/log/zap-scan}"
LOG_FILE="${LOG_DIR}/cron-$(date +%Y%m%d).log"
ALERT_EMAIL="${ALERT_EMAIL:-admin@example.com}"
MAX_LOG_AGE_DAYS=90
MAX_REPORT_AGE_DAYS=90

# Ensure directories exist
mkdir -p "$LOG_DIR"
mkdir -p "$REPORTS_DIR"

# Lock file to prevent overlapping scans
LOCKFILE="/var/run/zap-scan.lock"
exec 200>"$LOCKFILE"
if ! flock -n 200; then
    echo "Another scan is already running. Exiting."
    exit 0
fi

# Run scan with logging
{
    echo "============================================"
    echo "ZAP Automated Scan"
    echo "============================================"
    echo "Started:      $(date)"
    echo "Targets File: $TARGETS_FILE"
    echo "Reports Dir:  $REPORTS_DIR"
    echo "============================================"
    echo ""

    # Run the CLI batch scan
    zap-scan batch \
        --config "$TARGETS_FILE" \
        --reports-dir "$REPORTS_DIR" \
        --delay 10

    EXIT_CODE=$?

    echo ""
    echo "============================================"
    echo "Scan Completed"
    echo "============================================"
    echo "Finished:   $(date)"
    echo "Exit Code:  $EXIT_CODE"
    echo "============================================"

    # Send alert based on exit code
    if [ $EXIT_CODE -eq 2 ]; then
        {
            echo "ZAP Security Scan Alert"
            echo "======================"
            echo ""
            echo "One or more scans FAILED during automated scanning."
            echo ""
            echo "Time: $(date)"
            echo "Targets: $TARGETS_FILE"
            echo ""
            echo "Please review the reports at: $REPORTS_DIR"
            echo ""
            echo "Log file: $LOG_FILE"
        } | mail -s "⚠️ ZAP Scan Alert: Failures Detected" "$ALERT_EMAIL"
    elif [ $EXIT_CODE -eq 1 ]; then
        {
            echo "ZAP Security Scan Warning"
            echo "========================"
            echo ""
            echo "Scans completed with WARNINGS."
            echo ""
            echo "Time: $(date)"
            echo "Targets: $TARGETS_FILE"
            echo ""
            echo "Please review the reports at: $REPORTS_DIR"
        } | mail -s "⚠️ ZAP Scan: Warnings Detected" "$ALERT_EMAIL"
    fi

    # Cleanup old logs
    echo ""
    echo "Cleaning up old logs (>${MAX_LOG_AGE_DAYS} days)..."
    find "$LOG_DIR" -type f -name "cron-*.log" -mtime +${MAX_LOG_AGE_DAYS} -delete

    # Cleanup old reports (optional)
    echo "Cleaning up old reports (>${MAX_REPORT_AGE_DAYS} days)..."
    find "$REPORTS_DIR" -type f -mtime +${MAX_REPORT_AGE_DAYS} -delete
    find "$REPORTS_DIR" -type d -empty -delete

    echo "Cleanup complete."

    exit $EXIT_CODE

} 2>&1 | tee -a "$LOG_FILE"
```

Make it executable:
```bash
chmod +x /usr/local/bin/zap-cron-scan.sh
```

## Cron Examples

### Daily Scans

```cron
# Daily at 2 AM
0 2 * * * /usr/local/bin/zap-cron-scan.sh

# Daily at 2 AM with specific targets
0 2 * * * TARGETS_FILE=/opt/zap-scanner/daily-targets.txt /usr/local/bin/zap-cron-scan.sh

# Twice daily (2 AM and 2 PM)
0 2,14 * * * /usr/local/bin/zap-cron-scan.sh
```

### Weekly Scans

```cron
# Weekly on Sunday at 3 AM
0 3 * * 0 /usr/local/bin/zap-cron-scan.sh

# Weekly with full scans
0 3 * * 0 zap-scan batch --config /opt/zap-scanner/weekly-targets.txt --delay 15
```

### Monthly Scans

```cron
# First day of month at 4 AM
0 4 1 * * /usr/local/bin/zap-cron-scan.sh

# Last Sunday of month
0 3 22-28 * 0 /usr/local/bin/zap-cron-scan.sh
```

## Environment Variables

Set these in your wrapper script or crontab:

```bash
# In crontab
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
TARGETS_FILE=/opt/zap-scanner/targets.txt
REPORTS_DIR=/opt/zap-scanner/reports
ALERT_EMAIL=security@example.com

# Then your cron jobs...
0 2 * * * /usr/local/bin/zap-cron-scan.sh
```

## Monitoring and Alerting

### Health Checks

Use a service like [Healthchecks.io](https://healthchecks.io) to monitor cron execution:

```bash
#!/bin/bash
HEALTHCHECK_URL="https://hc-ping.com/your-uuid-here"

# Ping start
curl -fsS --retry 3 "$HEALTHCHECK_URL/start" > /dev/null

# Run scan
zap-scan batch --config /path/to/targets.txt
EXIT_CODE=$?

# Ping completion (or failure)
if [ $EXIT_CODE -eq 0 ]; then
    curl -fsS --retry 3 "$HEALTHCHECK_URL" > /dev/null
else
    curl -fsS --retry 3 "$HEALTHCHECK_URL/fail" > /dev/null
fi
```

### Logging Best Practices

1. **Separate log per day**: Use date in filename for easy rotation
2. **Keep logs for 90 days**: Balance between history and disk space
3. **Log both stdout and stderr**: Use `2>&1 | tee -a`
4. **Include timestamps**: Helps with debugging timing issues

### Email Alerts

Configure `mail` command (requires `mailutils` or similar):

```bash
# Ubuntu/Debian
sudo apt-get install mailutils

# Configure in wrapper script
mail -s "Subject" admin@example.com < message.txt
```

Or use a more robust solution like sending via API:

```bash
# Example with curl to SendGrid, Mailgun, etc.
curl -X POST https://api.mailgun.net/v3/your-domain/messages \
    -u "api:YOUR-API-KEY" \
    -F from="scanner@your-domain.com" \
    -F to="admin@example.com" \
    -F subject="ZAP Scan Alert" \
    -F text="Scan completed with failures"
```

## Docker Considerations

### Resource Limits

ZAP scans run Docker containers which can be resource-intensive:

```bash
# Check Docker resource usage during scans
docker stats

# Set resource limits if needed (in your own Docker wrapper)
docker run --memory="2g" --cpus="2" ...
```

### Docker Socket Permissions

Ensure the cron user has access to Docker:

```bash
# Add user to docker group
sudo usermod -aG docker your-cron-user

# Or run with sudo (less secure)
0 2 * * * sudo -u docker-user /usr/local/bin/zap-cron-scan.sh
```

### Network Considerations

- Ensure the server has outbound access to target domains
- Consider using a proxy if scanning internal networks
- Check firewall rules for Docker containers

## Directory Structure

Recommended structure for production:

```
/opt/zap-scanner/
├── targets.txt              # Main targets file
├── daily-targets.txt        # Daily scan targets
├── weekly-targets.txt       # Weekly full scan targets
├── reports/                 # Scan reports
│   └── index.html          # Generated index
├── configs/                 # ZAP configuration files
│   └── domain_name/
│       └── zap.yaml
└── logs/                    # Cron logs (optional, or use /var/log)
    └── cron-20260111.log

/usr/local/bin/
└── zap-cron-scan.sh        # Wrapper script

/var/log/zap-scan/          # System logs
└── cron-20260111.log
```

## Report Management

### Automatic Cleanup

Old reports can accumulate quickly:

```bash
# In your wrapper script
# Keep reports for 90 days
find "$REPORTS_DIR" -type f -mtime +90 -delete
find "$REPORTS_DIR" -type d -empty -delete

# Or archive old reports
find "$REPORTS_DIR" -type d -mtime +30 -mtime -90 \
    -exec tar -czf {}.tar.gz {} \; \
    -exec rm -rf {} \;
```

### Report Rotation Strategy

```bash
# Keep daily reports for 30 days
# Keep weekly reports for 90 days
# Keep monthly reports for 1 year

# Example in cron wrapper
if [ "$(date +%d)" = "01" ]; then
    # Monthly scan - keep for 365 days
    TARGETS_FILE="/opt/zap-scanner/monthly-targets.txt"
elif [ "$(date +%u)" = "7" ]; then
    # Weekly scan - keep for 90 days
    TARGETS_FILE="/opt/zap-scanner/weekly-targets.txt"
else
    # Daily scan - keep for 30 days
    TARGETS_FILE="/opt/zap-scanner/daily-targets.txt"
fi
```

## Systemd Timer Alternative

For modern Linux systems, consider using systemd timers instead of cron:

**Service file** (`/etc/systemd/system/zap-scan.service`):
```ini
[Unit]
Description=ZAP Security Scan
After=network.target docker.service

[Service]
Type=oneshot
User=zap-scanner
WorkingDirectory=/opt/zap-scanner
Environment="TARGETS_FILE=/opt/zap-scanner/targets.txt"
Environment="REPORTS_DIR=/opt/zap-scanner/reports"
ExecStart=/usr/local/bin/zap-scan batch --config ${TARGETS_FILE} --reports-dir ${REPORTS_DIR}
StandardOutput=append:/var/log/zap-scan/scan.log
StandardError=append:/var/log/zap-scan/scan.log
```

**Timer file** (`/etc/systemd/system/zap-scan.timer`):
```ini
[Unit]
Description=Daily ZAP Security Scan
Requires=zap-scan.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable zap-scan.timer
sudo systemctl start zap-scan.timer

# Check status
sudo systemctl status zap-scan.timer
sudo systemctl list-timers
```

## Troubleshooting

### Cron Not Running

```bash
# Check cron service
sudo systemctl status cron

# Check cron logs
sudo tail -f /var/log/syslog | grep CRON

# Test manually
sudo -u cron-user /usr/local/bin/zap-cron-scan.sh
```

### Permission Issues

```bash
# Ensure proper ownership
sudo chown -R cron-user:cron-user /opt/zap-scanner

# Check Docker access
sudo -u cron-user docker ps
```

### PATH Issues in Cron

Cron runs with a minimal PATH. Always use full paths or set PATH in crontab:

```cron
PATH=/usr/local/bin:/usr/bin:/bin
SHELL=/bin/bash

0 2 * * * /usr/local/bin/zap-cron-scan.sh
```

## Security Considerations

1. **Credentials**: Store any API keys or credentials in environment files with restricted permissions
2. **User Isolation**: Run scans as a dedicated user with minimal privileges
3. **Log Rotation**: Implement proper log rotation to prevent disk fill
4. **Network Segmentation**: Consider running scans from a dedicated scanning network
5. **Rate Limiting**: Use appropriate delays between scans to avoid overwhelming targets

## See Also

- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [README.md](README.md) - Project overview
- [targets.txt](targets.txt) - Example targets file format
