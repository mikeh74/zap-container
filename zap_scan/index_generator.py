"""Generate HTML index for ZAP scan reports."""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ReportIndexGenerator:
    """Generate HTML index page for scan reports."""

    def __init__(self, reports_dir: str = "reports"):
        """Initialize with reports directory."""
        self.reports_dir = Path(reports_dir)

    def find_reports(self) -> Dict[str, List[Dict]]:
        """Find all reports organized by domain.

        Returns:
            Dictionary mapping domain names to list of report info dicts.
        """
        reports_by_domain = {}

        if not self.reports_dir.exists():
            return reports_by_domain

        # Iterate through domain directories
        for domain_dir in self.reports_dir.iterdir():
            if not domain_dir.is_dir() or domain_dir.name == "index.html":
                continue

            domain_name = domain_dir.name
            reports = []

            # Iterate through date directories
            for date_dir in domain_dir.iterdir():
                if not date_dir.is_dir():
                    continue

                date_name = date_dir.name

                # Find all HTML reports
                for html_report in date_dir.glob("*.html"):
                    report_name = html_report.stem
                    md_report = date_dir / f"{report_name}.md"
                    json_report = date_dir / f"{report_name}.json"

                    # Extract timestamp from filename
                    timestamp_match = re.search(r"(\d{8}_\d{6})", report_name)
                    if timestamp_match:
                        timestamp_str = timestamp_match.group(1)
                        formatted_time = f"{timestamp_str[:8]} {timestamp_str[9:11]}:{timestamp_str[11:13]}:{timestamp_str[13:15]}"
                    else:
                        formatted_time = "Unknown"

                    # Build relative paths
                    rel_html = f"{domain_name}/{date_name}/{report_name}.html"
                    rel_md = f"{domain_name}/{date_name}/{report_name}.md"
                    rel_json = f"{domain_name}/{date_name}/{report_name}.json"

                    reports.append(
                        {
                            "date": date_name,
                            "timestamp": formatted_time,
                            "timestamp_raw": timestamp_str if timestamp_match else "",
                            "html_path": rel_html,
                            "md_path": rel_md if md_report.exists() else None,
                            "json_path": rel_json if json_report.exists() else None,
                        }
                    )

            if reports:
                # Sort reports by timestamp (newest first)
                reports.sort(key=lambda x: x["timestamp_raw"], reverse=True)
                reports_by_domain[domain_name] = reports

        return reports_by_domain

    def generate_html(self) -> str:
        """Generate the HTML index page content."""
        reports_by_domain = self.find_reports()

        # Calculate statistics
        total_scans = sum(len(reports) for reports in reports_by_domain.values())
        total_domains = len(reports_by_domain)

        # Find last scan time
        last_scan = "Never"
        if total_scans > 0:
            all_timestamps = []
            for reports in reports_by_domain.values():
                for report in reports:
                    if report["timestamp_raw"]:
                        all_timestamps.append(report["timestamp_raw"])

            if all_timestamps:
                latest = max(all_timestamps)
                last_scan = f"{latest[:4]}-{latest[4:6]}-{latest[6:8]} {latest[9:11]}:{latest[11:13]}:{latest[13:15]}"

        # Generate HTML
        html = self._get_html_header()

        # Add domain sections
        if not reports_by_domain:
            html += '            <div class="no-reports">No scan reports found. Run a scan using zap-scan scan</div>\n'
        else:
            for domain_name, reports in sorted(reports_by_domain.items()):
                html += self._generate_domain_section(domain_name, reports)

        # Close HTML with statistics
        html += self._get_html_footer(total_scans, total_domains, last_scan)

        return html

    def _get_html_header(self) -> str:
        """Get the HTML header with CSS."""
        return """<!DOCTYPE html>
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
"""

    def _generate_domain_section(self, domain_name: str, reports: List[Dict]) -> str:
        """Generate HTML for a domain section."""
        html = f"""            <div class="domain-section">
                <div class="domain-header">
                    <span class="domain-name">{domain_name}</span>
                    <span class="scan-count">{len(reports)} scans</span>
                </div>
                <table class="reports-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Timestamp</th>
                            <th>Reports</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        for report in reports:
            html += f"""                        <tr>
                            <td>{report["date"]}</td>
                            <td class="timestamp">{report["timestamp"]}</td>
                            <td>
                                <a href="{report["html_path"]}" class="html-link" target="_blank">📄 HTML</a>
"""
            if report["md_path"]:
                html += f'                                <a href="{report["md_path"]}" class="md-link" target="_blank">📝 Markdown</a>\n'

            if report["json_path"]:
                html += f'                                <a href="{report["json_path"]}" class="json-link" target="_blank">📊 JSON</a>\n'

            html += "                            </td>\n"
            html += "                        </tr>\n"

        html += """                    </tbody>
                </table>
            </div>
"""
        return html

    def _get_html_footer(self, total_scans: int, total_domains: int, last_scan: str) -> str:
        """Get the HTML footer with statistics."""
        generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""        </div>

        <footer>
            <p>Generated on {generated_time} | OWASP ZAP Security Testing</p>
        </footer>
    </div>

    <script>
        document.getElementById('total-scans').textContent = '{total_scans}';
        document.getElementById('total-domains').textContent = '{total_domains}';
        document.getElementById('last-scan').textContent = '{last_scan}';
    </script>
</body>
</html>
"""

    def generate_index(self) -> str:
        """Generate and save the HTML index file.

        Returns:
            Path to the generated index file.
        """
        # Ensure reports directory exists
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Generate HTML content
        html_content = self.generate_html()

        # Write to file
        index_file = self.reports_dir / "index.html"
        with open(index_file, "w") as f:
            f.write(html_content)

        # Calculate statistics for output
        reports_by_domain = self.find_reports()
        total_scans = sum(len(reports) for reports in reports_by_domain.values())
        total_domains = len(reports_by_domain)

        print(f"✓ Index generated: {index_file}")
        print()
        print(f"Total scans: {total_scans}")
        print(f"Total domains: {total_domains}")

        return str(index_file)
