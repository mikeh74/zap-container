#!/bin/bash

# Generate HTML Index for ZAP Reports
# This script scans all reports and creates an index.html file

set -e

REPORTS_DIR="reports"
INDEX_FILE="${REPORTS_DIR}/index.html"

echo "Generating ZAP Reports Index..."

# Create reports directory if it doesn't exist
mkdir -p "${REPORTS_DIR}"

# Start HTML
cat > "${INDEX_FILE}" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZAP Security Scan Reports</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }
        
        header {
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #007bff;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2em;
            margin-bottom: 5px;
        }
        
        .stat-card p {
            opacity: 0.9;
            font-size: 0.9em;
        }
        
        .domain-section {
            margin-bottom: 40px;
        }
        
        .domain-header {
            background: #f8f9fa;
            padding: 15px 20px;
            border-left: 4px solid #007bff;
            margin-bottom: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 4px;
        }
        
        .domain-header:hover {
            background: #e9ecef;
        }
        
        .domain-name {
            font-size: 1.5em;
            font-weight: bold;
            color: #007bff;
        }
        
        .scan-count {
            background: #007bff;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .reports-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background: white;
        }
        
        .reports-table th {
            background: #007bff;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        .reports-table td {
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .reports-table tr:hover {
            background: #f8f9fa;
        }
        
        .report-link {
            color: #007bff;
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
            margin-right: 10px;
        }
        
        .report-link:hover {
            background: #e7f3ff;
            text-decoration: underline;
        }
        
        .html-link {
            background: #28a745;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            text-decoration: none;
            display: inline-block;
            font-size: 0.9em;
        }
        
        .html-link:hover {
            background: #218838;
        }
        
        .md-link {
            background: #6c757d;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            text-decoration: none;
            display: inline-block;
            font-size: 0.9em;
        }
        
        .md-link:hover {
            background: #5a6268;
        }
        
        .json-link {
            background: #17a2b8;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            text-decoration: none;
            display: inline-block;
            font-size: 0.9em;
        }
        
        .json-link:hover {
            background: #138496;
        }
        
        .timestamp {
            color: #666;
            font-size: 0.9em;
        }
        
        footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        
        .no-reports {
            text-align: center;
            padding: 40px;
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔒 ZAP Security Scan Reports</h1>
            <p class="subtitle">OWASP ZAP Security Testing Dashboard</p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <h3 id="total-scans">0</h3>
                <p>Total Scans</p>
            </div>
            <div class="stat-card">
                <h3 id="total-domains">0</h3>
                <p>Domains Tested</p>
            </div>
            <div class="stat-card">
                <h3 id="last-scan">Never</h3>
                <p>Last Scan</p>
            </div>
        </div>
        
        <div id="reports-container">
EOF

# Count totals
TOTAL_SCANS=0
TOTAL_DOMAINS=0
LAST_SCAN_TIME=""

# Find all domains
if [ -d "${REPORTS_DIR}" ]; then
    for domain_dir in "${REPORTS_DIR}"/*/; do
        if [ -d "$domain_dir" ]; then
            DOMAIN=$(basename "$domain_dir")
            
            # Skip if it's not a domain directory
            if [ "$DOMAIN" = "index.html" ]; then
                continue
            fi
            
            TOTAL_DOMAINS=$((TOTAL_DOMAINS + 1))
            SCAN_COUNT=0
            
            echo "            <div class=\"domain-section\">" >> "${INDEX_FILE}"
            echo "                <div class=\"domain-header\">" >> "${INDEX_FILE}"
            echo "                    <span class=\"domain-name\">$DOMAIN</span>" >> "${INDEX_FILE}"
            echo "                    <span class=\"scan-count\" id=\"count-$DOMAIN\">0 scans</span>" >> "${INDEX_FILE}"
            echo "                </div>" >> "${INDEX_FILE}"
            echo "                <table class=\"reports-table\">" >> "${INDEX_FILE}"
            echo "                    <thead>" >> "${INDEX_FILE}"
            echo "                        <tr>" >> "${INDEX_FILE}"
            echo "                            <th>Date</th>" >> "${INDEX_FILE}"
            echo "                            <th>Timestamp</th>" >> "${INDEX_FILE}"
            echo "                            <th>Reports</th>" >> "${INDEX_FILE}"
            echo "                        </tr>" >> "${INDEX_FILE}"
            echo "                    </thead>" >> "${INDEX_FILE}"
            echo "                    <tbody>" >> "${INDEX_FILE}"
            
            # Find all date folders for this domain
            for date_dir in "$domain_dir"*/; do
                if [ -d "$date_dir" ]; then
                    DATE=$(basename "$date_dir")
                    
                    # Find all HTML reports in this date folder
                    for html_report in "$date_dir"*.html; do
                        if [ -f "$html_report" ]; then
                            SCAN_COUNT=$((SCAN_COUNT + 1))
                            TOTAL_SCANS=$((TOTAL_SCANS + 1))
                            
                            REPORT_NAME=$(basename "$html_report" .html)
                            MD_REPORT="${date_dir}${REPORT_NAME}.md"
                            JSON_REPORT="${date_dir}${REPORT_NAME}.json"
                            
                            # Extract timestamp from filename
                            TIMESTAMP=$(echo "$REPORT_NAME" | grep -oE '[0-9]{8}_[0-9]{6}' || echo "")
                            if [ -n "$TIMESTAMP" ]; then
                                FORMATTED_TIME=$(echo "$TIMESTAMP" | sed 's/_/ /' | sed 's/\([0-9]\{8\}\) \([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1 \2:\3:\4/')
                            else
                                FORMATTED_TIME="Unknown"
                            fi
                            
                            # Update last scan time
                            if [ -z "$LAST_SCAN_TIME" ] || [ "$TIMESTAMP" \> "$LAST_SCAN_TIME" ]; then
                                LAST_SCAN_TIME="$TIMESTAMP"
                            fi
                            
                            REL_HTML_PATH="${domain_dir#${REPORTS_DIR}/}${DATE}/${REPORT_NAME}.html"
                            
                            echo "                        <tr>" >> "${INDEX_FILE}"
                            echo "                            <td>$DATE</td>" >> "${INDEX_FILE}"
                            echo "                            <td class=\"timestamp\">$FORMATTED_TIME</td>" >> "${INDEX_FILE}"
                            echo "                            <td>" >> "${INDEX_FILE}"
                            echo "                                <a href=\"$REL_HTML_PATH\" class=\"html-link\" target=\"_blank\">📄 HTML</a>" >> "${INDEX_FILE}"
                            
                            if [ -f "$MD_REPORT" ]; then
                                REL_MD_PATH="${domain_dir#${REPORTS_DIR}/}${DATE}/${REPORT_NAME}.md"
                                echo "                                <a href=\"$REL_MD_PATH\" class=\"md-link\" target=\"_blank\">📝 Markdown</a>" >> "${INDEX_FILE}"
                            fi
                            
                            if [ -f "$JSON_REPORT" ]; then
                                REL_JSON_PATH="${domain_dir#${REPORTS_DIR}/}${DATE}/${REPORT_NAME}.json"
                                echo "                                <a href=\"$REL_JSON_PATH\" class=\"json-link\" target=\"_blank\">📊 JSON</a>" >> "${INDEX_FILE}"
                            fi
                            
                            echo "                            </td>" >> "${INDEX_FILE}"
                            echo "                        </tr>" >> "${INDEX_FILE}"
                        fi
                    done
                fi
            done
            
            if [ $SCAN_COUNT -eq 0 ]; then
                echo "                        <tr><td colspan=\"3\" class=\"no-reports\">No scans found</td></tr>" >> "${INDEX_FILE}"
            fi
            
            echo "                    </tbody>" >> "${INDEX_FILE}"
            echo "                </table>" >> "${INDEX_FILE}"
            echo "            </div>" >> "${INDEX_FILE}"
            
            # Update scan count for this domain using JavaScript
            echo "            <script>document.getElementById('count-$DOMAIN').textContent = '$SCAN_COUNT scans';</script>" >> "${INDEX_FILE}"
        fi
    done
fi

if [ $TOTAL_DOMAINS -eq 0 ]; then
    echo "            <div class=\"no-reports\">No scan reports found. Run a scan using ./scan.sh</div>" >> "${INDEX_FILE}"
fi

# Format last scan time
if [ -n "$LAST_SCAN_TIME" ]; then
    FORMATTED_LAST_SCAN=$(echo "$LAST_SCAN_TIME" | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)_\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3 \4:\5:\6/')
else
    FORMATTED_LAST_SCAN="Never"
fi

# Close HTML
cat >> "${INDEX_FILE}" << EOF
        </div>
        
        <footer>
            <p>Generated on $(date '+%Y-%m-%d %H:%M:%S') | OWASP ZAP Security Testing</p>
        </footer>
    </div>
    
    <script>
        document.getElementById('total-scans').textContent = '$TOTAL_SCANS';
        document.getElementById('total-domains').textContent = '$TOTAL_DOMAINS';
        document.getElementById('last-scan').textContent = '$FORMATTED_LAST_SCAN';
    </script>
</body>
</html>
EOF

echo "✓ Index generated: ${INDEX_FILE}"
echo ""
echo "Total scans: $TOTAL_SCANS"
echo "Total domains: $TOTAL_DOMAINS"
echo "Last scan: $FORMATTED_LAST_SCAN"
echo ""
echo "Open in browser: open ${INDEX_FILE}"
