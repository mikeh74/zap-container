#!/bin/bash

# Scan multiple websites in batch
# Usage: ./scan-batch.sh [config-file]
# Config file format: one URL per line

set -e

CONFIG_FILE="${1:-targets.txt}"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    echo ""
    echo "Usage: $0 [config-file]"
    echo ""
    echo "Create a file with one URL per line:"
    echo "  https://www.example.com"
    echo "  https://api.example.com"
    echo "  https://app.example.com"
    echo ""
    exit 1
fi

# Read targets from file
mapfile -t TARGETS < "$CONFIG_FILE"

if [ ${#TARGETS[@]} -eq 0 ]; then
    echo "Error: No targets found in $CONFIG_FILE"
    exit 1
fi

echo "============================================"
echo "ZAP Batch Scanner"
echo "============================================"
echo "Config file: $CONFIG_FILE"
echo "Targets: ${#TARGETS[@]}"
echo "============================================"
echo ""

SUCCESSFUL=0
FAILED=0
WARNINGS=0

# Scan each target
for i in "${!TARGETS[@]}"; do
    target="${TARGETS[$i]}"
    
    # Skip empty lines and comments
    if [[ -z "$target" ]] || [[ "$target" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Extract scan type if specified (format: URL [scan-type])
    read -r url scan_type <<< "$target"
    scan_type="${scan_type:-baseline}"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "[$((i+1))/${#TARGETS[@]}] Scanning: $url"
    echo "Scan type: $scan_type"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if ./scan.sh "$url" "$scan_type"; then
        SUCCESSFUL=$((SUCCESSFUL + 1))
        echo "✓ Success"
    else
        exit_code=$?
        if [ $exit_code -eq 1 ]; then
            WARNINGS=$((WARNINGS + 1))
            echo "⚠ Completed with warnings"
        else
            FAILED=$((FAILED + 1))
            echo "✗ Failed"
        fi
    fi
    
    # Small delay between scans
    if [ $i -lt $((${#TARGETS[@]} - 1)) ]; then
        echo ""
        echo "Waiting 5 seconds before next scan..."
        sleep 5
    fi
done

echo ""
echo "============================================"
echo "Batch Scan Complete"
echo "============================================"
echo "Successful: $SUCCESSFUL"
echo "Warnings:   $WARNINGS"
echo "Failed:     $FAILED"
echo "Total:      ${#TARGETS[@]}"
echo "============================================"
echo ""

# Generate index
echo "Generating index page..."
./generate-index.sh

echo ""
echo "All done! Open reports/index.html to view results."
echo ""

# Return appropriate exit code
if [ $FAILED -gt 0 ]; then
    exit 2
elif [ $WARNINGS -gt 0 ]; then
    exit 1
else
    exit 0
fi
