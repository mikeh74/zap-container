"""Core scanning functionality for ZAP security scans."""

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional


class ScanType:
    """Available scan types."""

    BASELINE = "baseline"
    FULL = "full"
    API = "api"

    @classmethod
    def all_types(cls):
        """Return all available scan types."""
        return [cls.BASELINE, cls.FULL, cls.API]


class ZAPScanner:
    """Handle ZAP security scanning operations."""

    def __init__(self, reports_dir: str = "reports", configs_dir: str = "configs"):
        """Initialize the scanner with base directories."""
        self.reports_dir = Path(reports_dir)
        self.configs_dir = Path(configs_dir)

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL and clean it for directory names."""
        # Remove protocol
        domain = re.sub(r"^[^/]*//", "", url)
        # Remove path
        domain = re.sub(r"/.*$", "", domain)
        # Remove port
        domain = re.sub(r":.*$", "", domain)
        return domain

    def clean_domain_name(self, domain: str) -> str:
        """Convert domain to a clean directory name."""
        return domain.replace(".", "_")

    def get_config_file(self, domain_clean: str) -> Optional[Path]:
        """Get the config file path if it exists."""
        config_path = self.configs_dir / domain_clean / "zap.yaml"
        return config_path if config_path.exists() else None

    def create_report_dir(self, domain_clean: str) -> Path:
        """Create and return the report directory path."""
        date_folder = datetime.now().strftime("%Y-%m-%d")
        report_dir = self.reports_dir / domain_clean / date_folder
        report_dir.mkdir(parents=True, exist_ok=True)
        return report_dir

    def generate_report_names(self, domain_clean: str) -> tuple:
        """Generate report file names with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_base = f"{domain_clean}_{timestamp}"
        return (
            f"{report_base}.html",
            f"{report_base}.md",
            f"{report_base}.json",
        )

    def build_docker_command(
        self,
        url: str,
        scan_type: str,
        report_dir: Path,
        report_html: str,
        report_md: str,
        report_json: str,
        config_file: Optional[Path] = None,
    ) -> list:
        """Build the docker command for running ZAP scan."""
        cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{report_dir.absolute()}:/zap/wrk:rw",
        ]

        # Add config volume mount if config file exists
        if config_file:
            cmd.extend(["-v", f"{config_file.absolute()}:/zap/wrk/zap.yaml:ro"])

        cmd.extend(["ghcr.io/zaproxy/zaproxy:stable"])

        # Add scan type specific command
        if scan_type == ScanType.BASELINE:
            cmd.append("zap-baseline.py")
        elif scan_type == ScanType.FULL:
            cmd.append("zap-full-scan.py")
        elif scan_type == ScanType.API:
            cmd.extend(["zap-api-scan.py", "-f", "openapi"])
        else:
            raise ValueError(f"Unknown scan type: {scan_type}")

        # Add common arguments
        cmd.extend(
            [
                "-t",
                url,
                "-r",
                report_html,
                "-w",
                report_md,
                "-J",
                report_json,
            ]
        )

        # Add config file argument if present
        if config_file:
            cmd.extend(["-c", "/zap/wrk/zap.yaml"])

        return cmd

    def run_scan(self, url: str, scan_type: str = ScanType.BASELINE) -> int:
        """Run a ZAP security scan."""
        # Validate scan type
        if scan_type not in ScanType.all_types():
            raise ValueError(
                f"Invalid scan type: {scan_type}. Must be one of: {', '.join(ScanType.all_types())}"
            )

        # Extract and clean domain
        domain = self.extract_domain(url)
        domain_clean = self.clean_domain_name(domain)

        # Get config file if it exists
        config_file = self.get_config_file(domain_clean)

        # API scan requires config file
        if scan_type == ScanType.API and not config_file:
            raise ValueError("API scan requires a zap.yaml config file")

        # Create report directory
        report_dir = self.create_report_dir(domain_clean)

        # Generate report names
        report_html, report_md, report_json = self.generate_report_names(domain_clean)

        # Print scan information
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print("=" * 44)
        print("ZAP Security Scan")
        print("=" * 44)
        print(f"Target URL:    {url}")
        print(f"Domain:        {domain}")
        print(f"Scan Type:     {scan_type}")
        print(f"Report Dir:    {report_dir}")
        print(f"Timestamp:     {timestamp}")
        print("=" * 44)
        print()

        if config_file:
            print(f"Using custom config: {config_file}")
            print()

        # Build and run docker command
        cmd = self.build_docker_command(
            url, scan_type, report_dir, report_html, report_md, report_json, config_file
        )

        print(f"Running {scan_type} scan...")
        result = subprocess.run(cmd)

        # Print results
        print()
        print("=" * 44)
        if result.returncode == 0:
            print("✓ Scan completed successfully")
        elif result.returncode == 1:
            print("⚠ Scan completed with warnings")
        elif result.returncode == 2:
            print("✗ Scan failed")
        else:
            print(f"? Scan completed with status: {result.returncode}")
        print("=" * 44)
        print(f"Reports saved to: {report_dir}")
        print(f"  - HTML: {report_html}")
        print(f"  - Markdown: {report_md}")
        print(f"  - JSON: {report_json}")
        print("=" * 44)
        print()

        return result.returncode
