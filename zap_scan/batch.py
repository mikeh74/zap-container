"""Batch scanning functionality for multiple targets."""

import time
from pathlib import Path
from typing import List, Tuple

import yaml

from .scanner import ScanType, ZAPScanner


class BatchScanner:
    """Handle batch scanning of multiple targets."""

    def __init__(self, scanner: ZAPScanner):
        """Initialize batch scanner with a ZAPScanner instance."""
        self.scanner = scanner

    def read_targets(self, config_file: str) -> List[Tuple[str, str]]:
        """Read targets from config file.

        Supports both .txt and .yaml formats.
        - .txt format: URL [scan-type] per line
        - .yaml format: structured YAML with targets list

        Returns list of tuples (url, scan_type).
        """
        targets = []
        config_path = Path(config_file)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        # Determine format based on file extension
        if config_path.suffix.lower() in [".yaml", ".yml"]:
            targets = self._read_yaml_targets(config_path)
        else:
            # Default to text format for backward compatibility
            targets = self._read_text_targets(config_path)

        return targets

    def _read_text_targets(self, config_path: Path) -> List[Tuple[str, str]]:
        """Read targets from plain text format.

        Format: URL [scan-type] per line
        """
        targets = []
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse line (format: URL [scan-type])
                parts = line.split()
                if len(parts) == 0:
                    continue

                url = parts[0]
                scan_type = parts[1] if len(parts) > 1 else ScanType.BASELINE

                targets.append((url, scan_type))

        return targets

    def _read_yaml_targets(self, config_path: Path) -> List[Tuple[str, str]]:
        """Read targets from YAML format.

        Expected format:
        targets:
          - url: https://example.com
            scan_type: baseline
          - url: https://api.example.com
            scan_type: full
        """
        targets = []
        with open(config_path, "r") as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Failed to parse YAML config: {e}")

        if not config or "targets" not in config:
            raise ValueError("YAML config must contain 'targets' key")

        if not isinstance(config["targets"], list):
            raise ValueError("YAML 'targets' must be a list")

        for item in config["targets"]:
            if not isinstance(item, dict):
                raise ValueError(f"Each target must be a dictionary, got: {type(item)}")

            if "url" not in item:
                raise ValueError("Each target must have a 'url' field")

            url = item["url"]
            scan_type = item.get("scan_type", ScanType.BASELINE)

            # Validate scan type
            if scan_type not in ScanType.all_types():
                raise ValueError(
                    f"Invalid scan type '{scan_type}' for {url}. "
                    f"Must be one of: {', '.join(ScanType.all_types())}"
                )

            targets.append((url, scan_type))

        return targets

    def run_batch_scan(self, config_file: str, delay: int = 5) -> dict:
        """Run batch scan on multiple targets.

        Args:
            config_file: Path to file containing target URLs
            delay: Delay in seconds between scans

        Returns:
            Dictionary with scan results statistics
        """
        targets = self.read_targets(config_file)

        if not targets:
            raise ValueError(f"No targets found in {config_file}")

        print("=" * 44)
        print("ZAP Batch Scanner")
        print("=" * 44)
        print(f"Config file: {config_file}")
        print(f"Targets: {len(targets)}")
        print("=" * 44)
        print()

        successful = 0
        warnings = 0
        failed = 0

        for i, (url, scan_type) in enumerate(targets, 1):
            print()
            print("━" * 44)
            print(f"[{i}/{len(targets)}] Scanning: {url}")
            print(f"Scan type: {scan_type}")
            print("━" * 44)
            print()

            try:
                exit_code = self.scanner.run_scan(url, scan_type)

                if exit_code == 0:
                    successful += 1
                    print("✓ Success")
                elif exit_code == 1:
                    warnings += 1
                    print("⚠ Completed with warnings")
                else:
                    failed += 1
                    print("✗ Failed")

            except Exception as e:
                failed += 1
                print(f"✗ Error: {e}")

            # Add delay between scans (except after last scan)
            if i < len(targets):
                print()
                print(f"Waiting {delay} seconds before next scan...")
                time.sleep(delay)

        print()
        print("=" * 44)
        print("Batch Scan Complete")
        print("=" * 44)
        print(f"Successful: {successful}")
        print(f"Warnings:   {warnings}")
        print(f"Failed:     {failed}")
        print(f"Total:      {len(targets)}")
        print("=" * 44)
        print()

        return {
            "successful": successful,
            "warnings": warnings,
            "failed": failed,
            "total": len(targets),
        }
