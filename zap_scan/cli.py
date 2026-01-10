"""Command-line interface for ZAP scan tool."""

import sys

import click

from . import __version__
from .batch import BatchScanner
from .index_generator import ReportIndexGenerator
from .scanner import ZAPScanner
from .server import ReportServer


@click.group()
@click.version_option(version=__version__)
def main():
    """ZAP Scan - A CLI tool for running OWASP ZAP security scans.

    This tool provides an easy way to run ZAP security scans, manage reports,
    and view results in a web interface.
    """
    pass


@main.command()
@click.argument("url")
@click.option(
    "--scan-type",
    "-t",
    type=click.Choice(["baseline", "full", "api"], case_sensitive=False),
    default="baseline",
    help="Type of scan to run (baseline, full, or api)",
)
@click.option(
    "--reports-dir",
    "-r",
    default="reports",
    help="Directory to store reports (default: reports)",
)
@click.option(
    "--configs-dir",
    "-c",
    default="configs",
    help="Directory containing config files (default: configs)",
)
def scan(url, scan_type, reports_dir, configs_dir):
    """Run a ZAP security scan on a target URL.

    Examples:

        \b
        # Quick baseline scan
        zap-scan scan https://www.example.com

        \b
        # Full active scan
        zap-scan scan https://www.example.com --scan-type full

        \b
        # API scan (requires config)
        zap-scan scan https://api.example.com --scan-type api
    """
    scanner = ZAPScanner(reports_dir=reports_dir, configs_dir=configs_dir)

    try:
        exit_code = scanner.run_scan(url, scan_type)
        print()
        print("💡 Generate index page with: zap-scan generate-index")
        print("💡 Serve reports with: zap-scan serve")
        print()
        sys.exit(exit_code)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--config",
    "-c",
    default="targets.txt",
    help="Config file with target URLs (default: targets.txt)",
)
@click.option(
    "--delay",
    "-d",
    type=int,
    default=5,
    help="Delay between scans in seconds (default: 5)",
)
@click.option(
    "--reports-dir",
    "-r",
    default="reports",
    help="Directory to store reports (default: reports)",
)
@click.option(
    "--configs-dir",
    default="configs",
    help="Directory containing config files (default: configs)",
)
def batch(config, delay, reports_dir, configs_dir):
    """Run batch scans on multiple targets from a config file.

    The config file should contain one URL per line, optionally followed
    by the scan type (baseline, full, or api).

    Example config file format:

        \b
        https://www.example.com
        https://www.example.com baseline
        https://api.example.com full

    Examples:

        \b
        # Scan targets from default file (targets.txt)
        zap-scan batch

        \b
        # Scan targets from custom file
        zap-scan batch --config my-targets.txt

        \b
        # Use custom delay between scans
        zap-scan batch --delay 10
    """
    scanner = ZAPScanner(reports_dir=reports_dir, configs_dir=configs_dir)
    batch_scanner = BatchScanner(scanner)

    try:
        results = batch_scanner.run_batch_scan(config, delay)

        # Generate index automatically after batch scan
        print("Generating index page...")
        generator = ReportIndexGenerator(reports_dir)
        generator.generate_index()

        print()
        print("All done! Open reports/index.html to view results.")
        print("Or run: zap-scan serve")
        print()

        # Exit with appropriate code
        if results["failed"] > 0:
            sys.exit(2)
        elif results["warnings"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--reports-dir",
    "-r",
    default="reports",
    help="Directory containing reports (default: reports)",
)
def generate_index(reports_dir):
    """Generate an HTML index page for all scan reports.

    This command scans the reports directory and creates an index.html file
    that provides a nice web interface to browse all reports.

    Examples:

        \b
        # Generate index with default reports directory
        zap-scan generate-index

        \b
        # Generate index for custom reports directory
        zap-scan generate-index --reports-dir my-reports
    """
    try:
        generator = ReportIndexGenerator(reports_dir)
        index_path = generator.generate_index()

        print()
        print(f"Open in browser: {index_path}")
        print("Or run: zap-scan serve")
        print()

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--port",
    "-p",
    type=int,
    default=8000,
    help="Port to run the server on (default: 8000)",
)
@click.option(
    "--reports-dir",
    "-r",
    default="reports",
    help="Directory containing reports (default: reports)",
)
def serve(port, reports_dir):
    """Start an HTTP server to view reports in a browser.

    This starts a simple web server that serves the reports directory,
    allowing you to view the index page and all reports in your browser.

    Examples:

        \b
        # Serve reports on default port (8000)
        zap-scan serve

        \b
        # Serve reports on custom port
        zap-scan serve --port 8080

        \b
        # Serve custom reports directory
        zap-scan serve --reports-dir my-reports
    """
    try:
        server = ReportServer(reports_dir, port)
        server.serve()
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
