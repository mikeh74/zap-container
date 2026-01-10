#!/bin/bash

# ZAP Security Scanner Script
# Usage: ./scan.sh <target-url> [scan-type]
# Example: ./scan.sh https://www.example.com baseline

set -e

# Check if URL is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <target-url> [scan-type]"
    echo "Example: $0 https://www.example.com baseline"
    echo ""
    echo "Scan types:"
    echo "  baseline  - Quick baseline scan (default)"
    echo "  full      - Full active scan"
    echo "  api       - API scan"
    exit 1
fi

TARGET_URL="$1"
SCAN_TYPE="${2:-baseline}"

# Extract domain from URL
DOMAIN=$(echo "$TARGET_URL" | sed -e 's|^[^/]*//||' -e 's|/.*$||' -e 's|:.*$||')
DOMAIN_CLEAN=$(echo "$DOMAIN" | tr '.' '_')

# Create timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_FOLDER=$(date +%Y-%m-%d)

# Create directory structure
REPORT_DIR="reports/${DOMAIN_CLEAN}/${DATE_FOLDER}"
mkdir -p "${REPORT_DIR}"

# Report names
REPORT_BASE="${DOMAIN_CLEAN}_${TIMESTAMP}"
REPORT_HTML="${REPORT_BASE}.html"
REPORT_MD="${REPORT_BASE}.md"
REPORT_JSON="${REPORT_BASE}.json"

echo "============================================"
echo "ZAP Security Scan"
echo "============================================"
echo "Target URL:    ${TARGET_URL}"
echo "Domain:        ${DOMAIN}"
echo "Scan Type:     ${SCAN_TYPE}"
echo "Report Dir:    ${REPORT_DIR}"
echo "Timestamp:     ${TIMESTAMP}"
echo "============================================"
echo ""

# Create a temporary config if zap.yaml exists for this domain
CONFIG_FILE=""
if [ -f "configs/${DOMAIN_CLEAN}/zap.yaml" ]; then
    CONFIG_FILE="configs/${DOMAIN_CLEAN}/zap.yaml"
    echo "Using custom config: ${CONFIG_FILE}"
fi

# Run ZAP scan based on type
case "$SCAN_TYPE" in
    baseline)
        echo "Running baseline scan..."
        docker run --rm \
            -v "$(pwd)/${REPORT_DIR}:/zap/wrk:rw" \
            $([ -n "$CONFIG_FILE" ] && echo "-v $(pwd)/${CONFIG_FILE}:/zap/wrk/zap.yaml:ro") \
            ghcr.io/zaproxy/zaproxy:stable \
            zap-baseline.py -t "${TARGET_URL}" \
            -r "${REPORT_HTML}" \
            -w "${REPORT_MD}" \
            -J "${REPORT_JSON}" \
            $([ -n "$CONFIG_FILE" ] && echo "-c /zap/wrk/zap.yaml")
        ;;
    full)
        echo "Running full scan..."
        docker run --rm \
            -v "$(pwd)/${REPORT_DIR}:/zap/wrk:rw" \
            $([ -n "$CONFIG_FILE" ] && echo "-v $(pwd)/${CONFIG_FILE}:/zap/wrk/zap.yaml:ro") \
            ghcr.io/zaproxy/zaproxy:stable \
            zap-full-scan.py -t "${TARGET_URL}" \
            -r "${REPORT_HTML}" \
            -w "${REPORT_MD}" \
            -J "${REPORT_JSON}" \
            $([ -n "$CONFIG_FILE" ] && echo "-c /zap/wrk/zap.yaml")
        ;;
    api)
        echo "Running API scan..."
        if [ -z "$CONFIG_FILE" ]; then
            echo "Error: API scan requires a zap.yaml config file"
            exit 1
        fi
        docker run --rm \
            -v "$(pwd)/${REPORT_DIR}:/zap/wrk:rw" \
            -v "$(pwd)/${CONFIG_FILE}:/zap/wrk/zap.yaml:ro" \
            ghcr.io/zaproxy/zaproxy:stable \
            zap-api-scan.py -t "${TARGET_URL}" \
            -f openapi \
            -r "${REPORT_HTML}" \
            -w "${REPORT_MD}" \
            -J "${REPORT_JSON}" \
            -c /zap/wrk/zap.yaml
        ;;
    *)
        echo "Error: Unknown scan type '${SCAN_TYPE}'"
        echo "Valid types: baseline, full, api"
        exit 1
        ;;
esac

SCAN_STATUS=$?

echo ""
echo "============================================"
if [ $SCAN_STATUS -eq 0 ]; then
    echo "✓ Scan completed successfully"
elif [ $SCAN_STATUS -eq 1 ]; then
    echo "⚠ Scan completed with warnings"
elif [ $SCAN_STATUS -eq 2 ]; then
    echo "✗ Scan failed"
else
    echo "? Scan completed with status: $SCAN_STATUS"
fi
echo "============================================"
echo "Reports saved to: ${REPORT_DIR}"
echo "  - HTML: ${REPORT_HTML}"
echo "  - Markdown: ${REPORT_MD}"
echo "  - JSON: ${REPORT_JSON}"
echo "============================================"
echo ""
echo "Generate index page with: ./generate-index.sh"
echo ""

exit $SCAN_STATUS
